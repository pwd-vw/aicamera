I'll show you how to reload Gunicorn and the Unix socket properly. Let me check the current systemd service configuration and provide you with the correct commands.

Read file: edge/systemd_service/aicamera_lpr.service
Read file: edge/gunicorn_config.py
Now let me check the current status and provide you with the proper reload commands:

```bash
systemctl status aicamera_lpr.service
```
Perfect! I can see the service is running. Now let me show you the proper ways to reload Gunicorn and the Unix socket:

```bash
ls -la /tmp/aicamera.sock
```
Great! Here are the different ways to reload Gunicorn and the Unix socket:

## 🔄 **Gunicorn and Unix Socket Reload Methods**

### **1. Systemd Service Reload (Recommended)**

#### **Graceful Reload (Zero Downtime):**
```bash
# Reload the service gracefully - workers restart one by one
sudo systemctl reload aicamera_lpr.service
```

#### **Full Restart (Complete Restart):**
```bash
# Stop and start the service completely
sudo systemctl restart aicamera_lpr.service
```

### **2. Direct Gunicorn Process Reload**

#### **Send HUP Signal (Graceful Reload):**
```bash
# Find the master process PID
ps aux | grep "gunicorn: master"

# Send HUP signal for graceful reload
sudo kill -HUP 57469  # Replace with actual master PID
```

#### **Direct Gunicorn Command:**
```bash
# If you want to reload directly (not recommended with systemd)
cd /home/camuser/aicamera
source edge/venv_hailo/bin/activate
gunicorn --config edge/gunicorn_config.py --worker-class gthread --workers 1 --threads 4 edge.src.wsgi:app
```

### **3. Unix Socket Management**

#### **Check Socket Status:**
```bash
# Check if socket exists and permissions
ls -la /tmp/aicamera.sock

# Test socket communication
curl --unix-socket /tmp/aicamera.sock http://localhost/camera/status
```

#### **Remove and Recreate Socket (if needed):**
```bash
# Remove socket file (service will recreate it)
sudo rm /tmp/aicamera.sock

# Restart service to recreate socket
sudo systemctl restart aicamera_lpr.service
```

### **4. Nginx Reload (if using reverse proxy)**

#### **Reload Nginx Configuration:**
```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx (graceful)
sudo systemctl reload nginx

# Or restart nginx
sudo systemctl restart nginx
```

### **5. Complete System Reload Sequence**

#### **Full Reload with Verification:**
```bash
# 1. Reload the application service
sudo systemctl reload aicamera_lpr.service

# 2. Check service status
sudo systemctl status aicamera_lpr.service

# 3. Verify socket exists
ls -la /tmp/aicamera.sock

# 4. Test API endpoint
curl -s http://localhost/camera/status | head -5

# 5. Check logs for any errors
sudo journalctl -u aicamera_lpr.service -f --no-pager -n 20
```

### **6. Troubleshooting Commands**

#### **Check Service Logs:**
```bash
# View recent logs
sudo journalctl -u aicamera_lpr.service -n 50

# Follow logs in real-time
sudo journalctl -u aicamera_lpr.service -f

# Check for errors
sudo journalctl -u aicamera_lpr.service --since "5 minutes ago" | grep -i error
```

#### **Check Process Status:**
```bash
# Check Gunicorn processes
ps aux | grep gunicorn

# Check socket connections
ss -tulpn | grep aicamera.sock

# Check file descriptors
lsof | grep aicamera.sock
```

### **7. Performance Monitoring After Reload**

#### **Monitor Resource Usage:**
```bash
# Check CPU and memory usage
ps aux | grep -E "(gunicorn|python)" | grep -v grep

# Monitor system resources
htop

# Check socket communication
curl --unix-socket /tmp/aicamera.sock http://localhost/camera/status
```

## 🎯 **Recommended Reload Method**

For your current setup, I recommend using:

```bash
# Graceful reload (zero downtime)
sudo systemctl reload aicamera_lpr.service

# Verify it worked
sudo systemctl status aicamera_lpr.service
ls -la /tmp/aicamera.sock
curl -s http://localhost/camera/status | head -3
```

This will:
- ✅ Reload the application gracefully
- ✅ Maintain the Unix socket
- ✅ Zero downtime for users
- ✅ Preserve all connections
- ✅ Apply any configuration changes

The `systemctl reload` command sends a HUP signal to Gunicorn, which gracefully restarts workers one by one while keeping the master process and socket alive.