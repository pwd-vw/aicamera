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
#   GATEWAY_IP      Override local gateway IP (default: 100.101.102.1)
#   GOOGLE_DNS_IP   Override Google DNS IP (default: 8.8.8.8)

DIR="/home/camuser/aicamera/network_diagnostics"
mkdir -p "$DIR"

TS="$(date -u +%Y%m%d_%H%M%SZ)"
LOG="$DIR/netdiag_$TS.log"
REPORT="$DIR/netdiag_$TS.md"
TMP="$DIR/tmp_$TS"
mkdir -p "$TMP"

GOOGLE_DNS_IP="${GOOGLE_DNS_IP:-8.8.8.8}"
GATEWAY_IP="${GATEWAY_IP:-100.101.102.1}"
LPR_IP="${TARGET_LPR_IP:-100.95.46.128}"

{
  echo "===== Network Diagnostics for aicamera1 Edge Device ====="
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
} | tee "$LOG" >/dev/null

# Build summary table from ping outputs
parse_ping() {
  local file="$1"; local name="$2"; local target="$3"
  local tx rx loss rtt
  tx=$(grep -E "packets transmitted" "$file" 2>/dev/null | awk '{print $1}')
  rx=$(grep -E "packets transmitted" "$file" 2>/dev/null | awk '{print $4}')
  loss=$(grep -E "packet loss" "$file" 2>/dev/null | sed -E 's/.* ([0-9.]+)% packet loss.*/\1%/')
  rtt=$(grep -E 'rtt min/avg/max|round-trip min/avg/max' "$file" 2>/dev/null | awk -F' = ' '{print $2}' | awk '{print $1}' | sed 's/ ms//')
  if [ -z "$tx" ]; then tx="-"; fi
  if [ -z "$rx" ]; then rx="-"; fi
  if [ -z "$loss" ]; then loss="-"; fi
  if [ -z "$rtt" ]; then rtt="-"; fi
  echo "| $name | $target | $tx | $rx | $loss | $rtt |"
}

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

  echo
  echo "### Notes"
  echo "- For Tailscale on LPR Server, verify status via the Tailscale admin console."
} > "$REPORT"

rm -rf "$TMP"

echo "Report: $REPORT"
echo "Log:    $LOG"


