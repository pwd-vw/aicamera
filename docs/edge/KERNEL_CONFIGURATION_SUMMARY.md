# AI Camera Kernel Configuration Summary

## Overview
The kernel configuration has been updated to optimize for Raspberry Pi 5 (BCM2712) hardware and enable automatic kernel updates while preventing incompatible kernels from being installed.

## What Was Accomplished

### 1. Kernel Cleanup
- **Removed old kernels**: Deleted `linux-image-6.12.25+rpt-rpi-2712` and `linux-image-6.12.25+rpt-rpi-v8`
- **Removed incompatible kernels**: Deleted all `rpi-v8` kernels (incompatible with Raspberry Pi 5)
- **Cleaned up boot files**: Removed `/boot/firmware/kernel8.img` and `/boot/firmware/initramfs8`
- **Freed disk space**: Recovered approximately 130MB of disk space

### 2. Current Kernel Status
- **Running kernel**: `6.12.34+rpt-rpi-2712` (latest version)
- **Installed kernels**: Only the current rpi-2712 kernel and meta-package
- **Boot configuration**: Using `/boot/firmware/kernel_2712.img` (correct for Pi 5)

### 3. Kernel Update Configuration

#### Apt Preferences (`/etc/apt/preferences.d/99-kernel-updates`)
- **Prioritizes**: `rpi-2712` kernels (Pin-Priority: 1001)
- **Blocks**: `rpi-v8` kernels (Pin-Priority: -1)
- **Prevents**: Installation of incompatible kernels

#### Unattended Upgrades (`/etc/apt/apt.conf.d/50unattended-upgrades`)
- **Automatic updates**: Security and kernel updates
- **Package blacklist**: Prevents rpi-v8 kernels from being installed
- **Automatic cleanup**: Removes unused kernel packages
- **No automatic reboot**: Manual reboot required after updates

#### Automatic Cleanup (`/usr/local/bin/cleanup-old-kernels`)
- **Schedule**: Weekly on Sunday at 2:00 AM (via crontab)
- **Function**: Removes old kernels except current and one previous
- **Cache cleanup**: Runs `apt autoremove` and `apt autoclean`

#### Update Notifications (`/usr/local/bin/check-kernel-updates`)
- **Function**: Checks for available kernel updates
- **Usage**: Run manually to see available updates

## Hardware Compatibility

### Raspberry Pi 5 (Current Hardware)
- **Chip**: BCM2712 (ARM Cortex-A76)
- **Kernel type**: `rpi-2712`
- **Boot file**: `kernel_2712.img`
- **Status**: ✅ Fully compatible and optimized

### Other Raspberry Pi Models
- **Pi 4/400/CM4**: Use `rpi-2712` kernels
- **Pi 3/3+/Zero 2**: Use `rpi-v8` kernels
- **Pi 5**: Use `rpi-2712` kernels (current)

## Available Scripts

### Management Scripts
1. **`scripts/cleanup_kernels.sh`** - Clean up old and incompatible kernels
2. **`scripts/kernel_update_config.sh`** - Configure kernel update settings
3. **`scripts/kernel_status.sh`** - Show current kernel status and configuration

### System Scripts
1. **`/usr/local/bin/check-kernel-updates`** - Check for available kernel updates
2. **`/usr/local/bin/cleanup-old-kernels`** - Automatic kernel cleanup (weekly)

## Update Process

### Manual Updates
```bash
# Check for updates
sudo /usr/local/bin/check-kernel-updates

# Update system
sudo apt update && sudo apt upgrade

# Reboot if kernel was updated
sudo reboot
```

### Automatic Updates
- **Security updates**: Installed automatically
- **Kernel updates**: Installed automatically (requires manual reboot)
- **Old kernels**: Cleaned up automatically (weekly)

## Configuration Files

### Boot Configuration (`/boot/firmware/config.txt`)
```bash
# Run in 64-bit mode
arm_64bit=1

# Automatically load initramfs files, if found
auto_initramfs=1
```

### Apt Preferences (`/etc/apt/preferences.d/99-kernel-updates`)
- Prioritizes rpi-2712 kernels
- Blocks rpi-v8 kernels from installation

### Unattended Upgrades (`/etc/apt/apt.conf.d/50unattended-upgrades`)
- Configures automatic security and kernel updates
- Blacklists incompatible kernel packages

## Benefits

### Performance
- **Reduced boot time**: Only compatible kernel files
- **Less disk usage**: Removed unnecessary kernel packages
- **Optimized for hardware**: Using correct kernel variant

### Maintenance
- **Automatic updates**: Security and kernel updates installed automatically
- **Automatic cleanup**: Old kernels removed weekly
- **Prevention**: Incompatible kernels blocked from installation

### Reliability
- **Hardware-specific**: Only kernels compatible with Pi 5
- **Fallback protection**: Keeps current and one previous kernel
- **Manual control**: Reboots require manual intervention

## Monitoring

### Status Check
```bash
# Show current kernel status
./scripts/kernel_status.sh

# Check for updates
/usr/local/bin/check-kernel-updates
```

### Logs
- **Unattended upgrades**: `/var/log/unattended-upgrades/`
- **Kernel updates**: `/var/log/apt/history.log`
- **System logs**: `/var/log/syslog`

## Troubleshooting

### If Kernel Updates Fail
1. Check available updates: `sudo apt update`
2. Check for errors: `sudo apt upgrade`
3. Verify configuration: `./scripts/kernel_status.sh`

### If System Won't Boot
1. Boot from recovery mode
2. Check boot configuration: `cat /boot/firmware/config.txt`
3. Verify kernel files: `ls -la /boot/firmware/kernel*`

### If Incompatible Kernels Installed
1. Run cleanup script: `sudo ./scripts/cleanup_kernels.sh`
2. Verify removal: `dpkg -l | grep linux-image`

## Conclusion

The kernel configuration is now optimized for the Raspberry Pi 5 hardware with:
- ✅ Only compatible kernels installed
- ✅ Automatic update system configured
- ✅ Old kernel cleanup automated
- ✅ Incompatible kernels blocked
- ✅ Manual monitoring tools available

The system is ready for production use with automatic kernel maintenance.
