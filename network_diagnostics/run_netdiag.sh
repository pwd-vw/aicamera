#!/usr/bin/env bash

set -euo pipefail

# Network diagnostics script for aicamera1 Edge Device
# Outputs a timestamped Markdown summary and a full log.
#
# Usage:
#   ./run_netdiag.sh
#
# Optional environment variables:
#   TARGET_LPR_IP   Override LPR Server IP (default: 100.95.46.128)
#   GATEWAY_IP      Override local gateway IP (default: 100.101.103.1)
#   GOOGLE_DNS_IP   Override Google DNS IP (default: 8.8.8.8)

DIR="/home/camuser/aicamera/network_diagnostics"
mkdir -p "$DIR"

TS="$(date -u +%Y%m%d_%H%M%SZ)"
LOG="$DIR/netdiag_$TS.log"
REPORT="$DIR/netdiag_$TS.md"
TMP="$DIR/tmp_$TS"
mkdir -p "$TMP"

GOOGLE_DNS_IP="${GOOGLE_DNS_IP:-8.8.8.8}"
# Auto-detect default gateway if not provided
raw_gw="$(ip route show default 2>/dev/null | awk '{print $3; exit}')"
# Sanitize: remove all non-digit and non-dot characters (including whitespace)
raw_gw="${raw_gw//[^0-9.]/}"
GATEWAY_IP="${GATEWAY_IP:-$raw_gw}"
if [ -z "${GATEWAY_IP// }" ]; then GATEWAY_IP="100.101.103.1"; fi
LPR_IP="${TARGET_LPR_IP:-100.95.46.128}"

{
  set +e
  echo "===== Network Diagnostics for $(hostname) Edge Device ====="
  echo "Timestamp (UTC): $TS"
  echo "Host: $(hostname) | Kernel: $(uname -srm)"
  echo
  echo "# 1) Initial network status"
  echo "## ip addr show"; ip addr show || true
  echo
  echo "## iwconfig"; (iwconfig 2>&1 || true)
  echo
  echo "## ip route show"; ip route show || true
  echo
  echo "# 2) Ping Google DNS ($GOOGLE_DNS_IP), 10 packets";
  (ping -c 10 "$GOOGLE_DNS_IP" | tee "$TMP/ping_google.txt") || true
  echo
  echo "# 3) Ping Local Gateway ($GATEWAY_IP), 10 packets";
  (ping -c 10 "$GATEWAY_IP" | tee "$TMP/ping_gw.txt") || true
  echo
  echo "# 4) Extended Latency Test to Google DNS ($GOOGLE_DNS_IP), 20 packets @ 0.2s";
  (ping -c 20 -i 0.2 "$GOOGLE_DNS_IP" | tee "$TMP/ping_google_ext.txt") || true
  echo
  echo "# 5) Tailscale status";
  (tailscale status 2>&1 || echo "tailscale status failed or tailscale not installed")
  (tailscale ip -4 2>&1 || true)
  echo
  echo "# 6) Extended Latency Test Edge -> LPRServer ($LPR_IP), 20 packets @ 0.2s";
  (ping -c 20 -i 0.2 "$LPR_IP" | tee "$TMP/ping_lpr.txt") || true
  echo
  echo "# 7) Interface statistics"
  echo "## /proc/net/dev"; cat /proc/net/dev || true
  echo
  echo "## ethtool eth0";
  (sudo -n ethtool eth0 2>/dev/null || ethtool eth0 2>&1 || echo "ethtool eth0 failed (insufficient perms or not installed)")
  echo
  echo "# 8) Recent kernel network logs (eth|wlan|network)";
  (dmesg | grep -i -E "eth|wlan|network" | tail -20 || true)
  set -e
} | tee "$LOG" >/dev/null

# Build summary table from ping outputs
parse_ping() {
  local file="$1"; local name="$2"; local target="$3"
  local tx rx loss rtt
  set +e
  tx=$(grep -E "packets transmitted" "$file" 2>/dev/null | awk '{print $1}') || true
  rx=$(grep -E "packets transmitted" "$file" 2>/dev/null | awk '{print $4}') || true
  loss=$(grep -E "packet loss" "$file" 2>/dev/null | sed -E 's/.* ([0-9.]+)% packet loss.*/\1%/') || true
  rtt=$(grep -E 'rtt min/avg/max|round-trip min/avg/max' "$file" 2>/dev/null | awk -F' = ' '{print $2}' | awk '{print $1}' | sed 's/ ms//') || true
  set -e
  if [ -z "$tx" ]; then tx="-"; fi
  if [ -z "$rx" ]; then rx="-"; fi
  if [ -z "$loss" ]; then loss="-"; fi
  if [ -z "$rtt" ]; then rtt="-"; fi
  echo "| $name | $target | $tx | $rx | $loss | $rtt |"
}

# Collect interface facts for the Markdown report
collect_iface_facts() {
  ETH_LINK=$(ip -o link show eth0 2>/dev/null | awk -F',|: ' '{print ($0 ~ /state UP/)?"UP":"DOWN"}')
  ETH_MAC=$(ip -o link show eth0 2>/dev/null | awk '{for(i=1;i<=NF;i++){if($i=="link/ether"){print $(i+1); break}}}')
  ETH_IPV4=$(ip -4 -o addr show dev eth0 2>/dev/null | awk '{print $4}' | paste -sd, -)
  ETH_IPV6=$(ip -6 -o addr show dev eth0 2>/dev/null | awk '{print $4}' | paste -sd, -)
  ETH_SPEED=$( (sudo -n ethtool eth0 2>/dev/null || ethtool eth0 2>/dev/null) | awk -F': ' '/Speed:/{print $2}')
  ETH_DUPLEX=$( (sudo -n ethtool eth0 2>/dev/null || ethtool eth0 2>/dev/null) | awk -F': ' '/Duplex:/{print $2}')

  WLAN_LINK=$(ip -o link show wlan0 2>/dev/null | awk -F',|: ' '{print ($0 ~ /state UP/)?"UP":"DOWN"}')
  WLAN_MAC=$(ip -o link show wlan0 2>/dev/null | awk '{for(i=1;i<=NF;i++){if($i=="link/ether"){print $(i+1); break}}}')
  WLAN_IPV4=$(ip -4 -o addr show dev wlan0 2>/dev/null | awk '{print $4}' | paste -sd, -)
  WLAN_IPV6=$(ip -6 -o addr show dev wlan0 2>/dev/null | awk '{print $4}' | paste -sd, -)
  WLAN_SSID=$(iwgetid -r 2>/dev/null || echo "-")
  WLAN_SIGNAL=$(iwconfig 2>/dev/null | awk '/wlan0/{f=1} f&&/Signal level/{print $0; f=0}')

  DNS_SERVERS=$(grep -E '^nameserver' /etc/resolv.conf 2>/dev/null | awk '{print $2}' | paste -sd, -)
  if [ -z "$DNS_SERVERS" ]; then DNS_SERVERS="-"; fi
}

collect_iface_facts

{
  echo "## Network Diagnostics Summary"
  echo
  echo "Log file: \`$LOG\`"
  echo
  echo "### Ping Summary"
  echo "| Test | Target | Sent | Received | Loss | Min/Avg/Max/mdev (ms) |"
  echo "|---|---|---:|---:|---:|---|"
  parse_ping "$TMP/ping_google.txt" "Ping Google (10x)" "$GOOGLE_DNS_IP"
  parse_ping "$TMP/ping_gw.txt" "Ping Gateway (10x)" "$GATEWAY_IP"
  parse_ping "$TMP/ping_google_ext.txt" "Extended Google (20x@0.2s)" "$GOOGLE_DNS_IP"
  parse_ping "$TMP/ping_lpr.txt" "Extended LPR (20x@0.2s)" "$LPR_IP"

  echo
  echo "### Interfaces"
  echo "- Default route: $(ip route show default 2>/dev/null | head -n1 | sed "s/^/\`/;s/$/\`/")"
  echo "- IP addresses: $(hostname -I 2>/dev/null | sed "s/^/\`/;s/$/\`/")"
  echo "- Tailscale IPv4: $(tailscale ip -4 2>/dev/null | paste -sd, - || echo -n "-")"
  echo "- DNS servers: \`$DNS_SERVERS\`"

  echo
  echo "### Interface Details"
  echo "| Interface | Link | MAC | IPv4 | IPv6 | Speed | Duplex |"
  echo "|---|---|---|---|---|---|---|"
  echo "| eth0 | ${ETH_LINK:--} | ${ETH_MAC:--} | ${ETH_IPV4:--} | ${ETH_IPV6:--} | ${ETH_SPEED:--} | ${ETH_DUPLEX:--} |"
  echo "| wlan0 | ${WLAN_LINK:--} | ${WLAN_MAC:--} | ${WLAN_IPV4:--} | ${WLAN_IPV6:--} | - | - |"
  echo
  echo "### Wi‑Fi Status"
  echo "- SSID: \`${WLAN_SSID:--}\`"
  echo "- Signal: \`${WLAN_SIGNAL:--}\`"

  echo
  echo "### Notes"
  echo "- For Tailscale on LPR Server, verify status via the Tailscale admin console."
} > "$REPORT"

rm -rf "$TMP"

echo "Report: $REPORT"
echo "Log:    $LOG"


