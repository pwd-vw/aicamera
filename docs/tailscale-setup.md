# Tailscale Network Setup Guide

## Overview

This guide explains how to set up and configure the AI Camera project to work with Tailscale network for secure, private communication between the LPR server and edge devices.

## Network Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LPR Server    │    │   Edge Device   │    │   Edge Device   │
│                 │    │                 │    │                 │
│ lprserver.      │◄──►│ aicamera1.      │◄──►│ aicamera2.      │
│ tail605477.ts.net│    │ tail605477.ts.net│    │ tail605477.ts.net│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Edge Device   │    │   Edge Device   │    │   Edge Device   │
│                 │    │                 │    │                 │
│ aicamera3.      │    │ aicamera4.      │    │ aicamera5.      │
│ tail605477.ts.net│    │ tail605477.ts.net│    │ tail605477.ts.net│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

1. **Tailscale Account**: Create an account at [tailscale.com](https://tailscale.com)
2. **Network Domain**: `tail605477.ts.net` (your Tailscale network)
3. **SSH Access**: SSH keys configured for all devices
4. **GitHub Secrets**: Configured SSH private keys

## Device Configuration

### LPR Server Setup

1. **Install Tailscale**:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```

2. **Configure Hostname**:
   ```bash
   sudo hostnamectl set-hostname lprserver
   ```

3. **Verify Connection**:
   ```bash
   tailscale status
   ping lprserver.tail605477.ts.net
   ```

### Edge Device Setup

For each edge device (aicamera1, aicamera2, aicamera3, aicamera4, aicamera5):

1. **Install Tailscale**:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```

2. **Configure Hostname** (replace DEVICE_NAME):
   ```bash
   sudo hostnamectl set-hostname aicamera1  # or aicamera2, etc.
   ```

3. **Verify Connection**:
   ```bash
   tailscale status
   ping aicamera1.tail605477.ts.net  # replace with device name
   ```

## GitHub Actions Configuration

### Required Secrets

Configure these secrets in your GitHub repository:

1. **SSH_PRIVATE_KEY**: SSH private key for deployment
2. **SERVER_USER**: Username for LPR server (e.g., `lpruser`)
3. **EDGE_USER**: Username for edge devices (e.g., `camuser`)

### Environment Variables

Set these repository variables:

1. **ENABLE_SERVER_DEPLOYMENT**: `true` to enable server deployment
2. **ENABLE_EDGE_DEPLOYMENT**: `true` to enable edge deployment

## Network Security

### Access Control Lists (ACLs)

Configure Tailscale ACLs for secure communication:

```json
{
  "tagOwners": {
    "tag:lpr-server": ["lprserver"],
    "tag:edge-devices": ["aicamera1", "aicamera2", "aicamera3", "aicamera4", "aicamera5"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["tag:edge-devices"],
      "dst": ["tag:lpr-server:3000"]
    },
    {
      "action": "accept",
      "src": ["tag:lpr-server"],
      "dst": ["tag:edge-devices:80"]
    }
  ]
}
```

### Firewall Configuration

Ensure these ports are open:

- **LPR Server**: Port 80 (Nginx proxy to NestJS unix socket), Port 22 (SSH)
- **Edge Devices**: Port 80 (Nginx proxy to Python gunicorn unix socket), Port 22 (SSH)

## Deployment Workflow

### Automatic Deployment

The system supports automatic deployment through GitHub Actions:

1. **Push to main**: Triggers automatic deployment
2. **Manual trigger**: Use workflow dispatch for manual deployment
3. **Selective deployment**: Choose specific devices or all devices

### Deployment Options

```yaml
workflow_dispatch:
  inputs:
    deploy_server: true/false      # Deploy LPR server
    deploy_edge: true/false        # Deploy edge devices
    target_edge: all/aicamera1/aicamera2/aicamera3/aicamera4/aicamera5
    single_edge_host: "custom.device.com"  # Custom device
```

## Health Monitoring

### Automatic Health Checks

The system includes automatic health monitoring:

- **Frequency**: Every 5 minutes
- **Checks**: All devices in the network
- **Alerts**: Automatic issue creation for failed devices
- **Status**: Real-time health status tracking

### Manual Health Check

```bash
# Check LPR server health (via nginx proxy)
curl -f http://lprserver.tail605477.ts.net/health

# Check edge device health (via nginx proxy)
curl -f http://aicamera1.tail605477.ts.net/health

# Check all devices
./scripts/check_network_health.sh
```

## Troubleshooting

### Common Issues

1. **DNS Resolution Failed**:
   ```bash
   # Check Tailscale status
   tailscale status
   
   # Restart Tailscale
   sudo systemctl restart tailscaled
   ```

2. **Service Not Responding**:
   ```bash
   # Check service status
   sudo systemctl status aicamera_lpr.service
   
   # Check logs
   sudo journalctl -u aicamera_lpr.service -f
   ```

3. **Network Connectivity**:
   ```bash
   # Test connectivity
   ping lprserver.tail605477.ts.net
   
   # Check firewall
   sudo ufw status
   ```

### Debug Commands

```bash
# Check Tailscale network
tailscale status
tailscale ping lprserver.tail605477.ts.net

# Check service health
curl -v http://lprserver.tail605477.ts.net:3000/health
curl -v http://aicamera1.tail605477.ts.net/health

# Check system resources
htop
df -h
free -h
```

## Monitoring Dashboard

Access the monitoring dashboard at:
- **LPR Server**: http://lprserver.tail605477.ts.net (NestJS API via nginx proxy)
- **Edge Devices**: http://aicamera1.tail605477.ts.net (Python edge via nginx proxy)

## Security Best Practices

1. **Regular Updates**: Keep Tailscale and system packages updated
2. **Access Control**: Use ACLs to restrict network access
3. **Monitoring**: Enable automatic health monitoring
4. **Backups**: Regular backups of configuration and data
5. **Logs**: Monitor system and application logs

## Support

For issues related to:
- **Tailscale**: Check [Tailscale documentation](https://tailscale.com/kb/)
- **AI Camera**: Check project documentation
- **Deployment**: Check GitHub Actions logs
- **Network**: Use health monitoring workflow
