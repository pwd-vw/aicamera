# 📁 Script Organization Guide

This document outlines the organized structure of scripts in the `/scripts` directory, categorized by objective and operation type using prefix naming conventions.

## 🏗️ **Organization Structure**

### **1. Setup & Installation Scripts (`setup_`)**
Scripts for initial setup, installation, and configuration of various system components.

| Script | Purpose | Description |
|--------|---------|-------------|
| `setup_github_runner.sh` | GitHub Actions Runner Setup | Sets up self-hosted GitHub Actions runner |
| `setup_github_secrets.sh` | GitHub Secrets Configuration | Configures GitHub repository secrets and variables |
| `setup_ssh_keys.sh` | SSH Key Management | Sets up SSH keys for secure communication |
| `setup_communication_system.sh` | Communication Infrastructure | Sets up MQTT broker, SFTP, and communication protocols |
| `setup_dev_environment.sh` | Development Environment | Sets up development environment for AI Camera project |
| `setup_dev_environment.ps1` | Windows Dev Environment | PowerShell version for Windows development setup |
| `setup_boot_logo.sh` | Boot Logo Configuration | Configures custom boot logo for Raspberry Pi |

### **2. System Management Scripts (`sys_`)**
Scripts for managing system services, monitoring, and control operations.

| Script | Purpose | Description |
|--------|---------|-------------|
| `sys_aicamera_control.sh` | AI Camera Service Control | Manages AI Camera backend and frontend services |
| `sys_monitor.sh` | System Monitoring | Comprehensive system monitoring and health checks |
| `sys_quick_monitor.sh` | Quick System Check | Fast system status check and basic monitoring |

### **3. Kernel Management Scripts (`kernel_`)**
Scripts specifically for kernel-related operations and maintenance.

| Script | Purpose | Description |
|--------|---------|-------------|
| `kernel_status.sh` | Kernel Status Report | Comprehensive kernel status and configuration report |
| `kernel_update_config.sh` | Kernel Update Configuration | Configures automatic kernel updates and preferences |
| `kernel_cleanup.sh` | Kernel Cleanup | Removes old and incompatible kernel versions |

### **4. Verification & Testing Scripts (`verify_`)**
Scripts for testing, verification, and validation of system components.

| Script | Purpose | Description |
|--------|---------|-------------|
| `verify_setup.sh` | Setup Verification | Verifies that all setup scripts completed successfully |
| `verify_communication_test.py` | Communication Testing | Tests MQTT and SFTP communication systems |
| `verify_licenses.sh` | License Verification | Checks and validates software licenses |
| `verify_boot_logo.sh` | Boot Logo Verification | Verifies boot logo configuration and display |

### **5. Utility Scripts (`util_`)**
General utility scripts for various maintenance and helper functions.

| Script | Purpose | Description |
|--------|---------|-------------|
| `util_version.sh` | Version Management | Manages project versioning and release information |
| `util_restore_boot_logo.sh` | Boot Logo Restoration | Restores default boot logo configuration |
| `util_complete_runner_setup.sh` | Runner Setup Completion | Completes GitHub Actions runner setup process |

## 🔍 **Usage Examples**

### **Initial Setup Workflow**
```bash
# 1. Setup development environment
./setup_dev_environment.sh

# 2. Setup communication system
./setup_communication_system.sh

# 3. Setup GitHub integration
./setup_github_runner.sh
./setup_github_secrets.sh
./setup_ssh_keys.sh

# 4. Verify setup
./verify_setup.sh
```

### **System Management Workflow**
```bash
# Quick system check
./sys_quick_monitor.sh

# Detailed system monitoring
./sys_monitor.sh

# Control AI Camera services
./sys_aicamera_control.sh start
./sys_aicamera_control.sh stop
./sys_aicamera_control.sh restart
```

### **Kernel Management Workflow**
```bash
# Check kernel status
./kernel_status.sh

# Configure kernel updates
./kernel_update_config.sh

# Clean up old kernels
./kernel_cleanup.sh
```

### **Verification Workflow**
```bash
# Test communication systems
python3 verify_communication_test.py

# Check licenses
./verify_licenses.sh

# Verify boot logo
./verify_boot_logo.sh
```

## 📋 **Script Dependencies**

### **Prerequisites**
- Most scripts require `bash` shell
- Some scripts require `sudo` privileges
- Python scripts require Python 3.x
- PowerShell scripts require Windows PowerShell 5.1+

### **Common Dependencies**
- `curl` - for API calls and downloads
- `jq` - for JSON processing
- `systemctl` - for service management
- `apt-get` or `yum` - for package management

## 🛠️ **Maintenance Guidelines**

### **Adding New Scripts**
1. **Choose appropriate prefix** based on script purpose
2. **Use descriptive names** that clearly indicate function
3. **Follow naming convention**: `prefix_descriptive_name.sh`
4. **Add documentation** in this README file
5. **Test thoroughly** before committing

### **Naming Conventions**
- **Use underscores** instead of hyphens for consistency
- **Use lowercase** for all script names
- **Keep names concise** but descriptive
- **Avoid special characters** except underscores

### **File Permissions**
- **Executable scripts**: `chmod +x script_name.sh`
- **Read-only documentation**: `chmod 644 README_*.md`
- **Configuration files**: `chmod 600 config_*.conf`

## 🔧 **Troubleshooting**

### **Common Issues**
1. **Permission Denied**: Ensure scripts have execute permissions
2. **Command Not Found**: Check if required dependencies are installed
3. **Sudo Required**: Some scripts require root privileges

### **Debug Mode**
Most scripts support verbose output. Add `-v` or `--verbose` flags:
```bash
./script_name.sh --verbose
```

## 📚 **Related Documentation**

- `../docs/edge/` - Edge device documentation
- `../docs/server/` - Server documentation
- `../docs/project/` - Project overview and architecture
- `../edge/README.md` - Edge application documentation

---

**Last Updated**: August 28, 2025  
**Version**: 1.0  
**Maintainer**: AI Camera Development Team
