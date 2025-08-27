# 🚀 AI Camera Development Environment - Quick Start Guide

## 📋 Overview

This guide provides step-by-step instructions to set up your development machine for the AI Camera monorepo project. The project includes:

- **Edge Components**: Python-based camera and AI processing
- **Server Components**: Node.js with NestJS backend  
- **Communication System**: MQTT, SFTP, WebSocket, REST API
- **Database**: PostgreSQL (server) and SQLite (edge)
- **Frontend**: Vue.js admin dashboard

## 🎯 Quick Setup Options

### Option 1: Automated Setup (Recommended)

#### For Linux/macOS:
```bash
# Clone the repository
git clone <your-repo-url> aicamera
cd aicamera

# Run automated setup
./scripts/setup_dev_environment.sh
```

#### For Windows:
```powershell
# Clone the repository
git clone <your-repo-url> aicamera
cd aicamera

# Run automated setup (as Administrator)
.\scripts\setup_dev_environment.ps1
```

### Option 2: Manual Setup

Follow the detailed guide in `DEVELOPMENT_SETUP_GUIDE.md`

## 🛠️ Required Software

### Core Requirements
- **Git**: Version control
- **Python 3.9+**: Edge development
- **Node.js 16+**: Server development
- **PostgreSQL**: Database
- **VS Code**: Code editor (recommended)

### Communication System
- **MQTT Broker**: Mosquitto
- **SSH/SFTP Server**: OpenSSH
- **Docker**: Containerization (optional)

## 📦 Installation Summary

### 1. System Dependencies
```bash
# Ubuntu/Debian
sudo apt install -y \
    python3 python3-pip python3-venv \
    nodejs npm \
    postgresql postgresql-contrib \
    mosquitto mosquitto-clients \
    openssh-server \
    git curl wget

# macOS
brew install \
    python@3.9 \
    node \
    postgresql@14 \
    mosquitto \
    openssh \
    git curl wget

# Windows
# Use Chocolatey or download installers manually
choco install python nodejs postgresql git
```

### 2. Python Environment (Edge)
```bash
cd edge
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
pip install paho-mqtt paramiko python-socketio requests pillow opencv-python numpy
```

### 3. Node.js Environment (Server)
```bash
cd server
npm install
npm install mqtt ssh2 ssh2-sftp-client socket.io @nestjs/websockets @nestjs/platform-socket.io
```

### 4. Database Setup
```bash
# PostgreSQL
sudo -u postgres createuser aicamera
sudo -u postgres createdb aicamera_db
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aicamera_db TO aicamera;"

# Server database
cd server
npx prisma generate
npx prisma db push

# Edge database
cd ../edge
python scripts/init_database.py
```

### 5. Communication Services
```bash
# Start MQTT broker
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Start SSH server
sudo systemctl start ssh
sudo systemctl enable ssh

# Create SFTP user
sudo useradd -m -s /bin/bash aicamera
echo "aicamera:aicamera123" | sudo chpasswd
```

## 🚀 Starting Development

### 1. Start All Services
```bash
# Terminal 1: Start Server
cd server
npm run start:dev

# Terminal 2: Start Frontend
cd frontend
npm run serve

# Terminal 3: Start Edge Simulator
cd edge/scripts
./run_simulator.sh  # Linux/macOS
# or
.\run_simulator.ps1  # Windows

# Terminal 4: Monitor Communication
mosquitto_sub -h localhost -t "aicamera/#"
```

### 2. Access Development Interfaces
- **Server API**: http://localhost:3000
- **Frontend Dashboard**: http://localhost:8080
- **API Documentation**: http://localhost:3000/api
- **Database Admin**: http://localhost:3000/prisma-studio

## 🧪 Testing the System

### 1. Test Registration Workflow
1. Edge simulator registers automatically
2. Check admin dashboard for pending approval
3. Approve device via web interface
4. Verify credentials distribution

### 2. Test Communication
```bash
# Monitor MQTT traffic
mosquitto_sub -h localhost -t "aicamera/#"

# Test SFTP connection
sftp aicamera@localhost

# Check image transfers
ls -la server/image_storage/
```

### 3. Run Automated Tests
```bash
# Test communication system
python scripts/test_communication_system.py

# Run edge tests
cd edge && python -m pytest tests/

# Run server tests
cd server && npm test
```

## 📁 Project Structure

```
aicamera/
├── edge/                    # Python edge components
│   ├── src/
│   │   ├── services/       # Edge services
│   │   ├── components/     # Edge components
│   │   └── core/          # Core functionality
│   ├── scripts/           # Edge scripts
│   ├── tests/             # Edge tests
│   └── venv/              # Python virtual environment
├── server/                 # Node.js server components
│   ├── src/
│   │   ├── device-registration/  # Device registration
│   │   ├── communication/        # Communication services
│   │   └── prisma/              # Database schema
│   ├── prisma/            # Database migrations
│   └── tests/             # Server tests
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   └── views/         # Vue views
│   └── public/            # Static assets
├── scripts/               # Setup and utility scripts
├── docs/                  # Documentation
└── logs/                  # Application logs
```

## 🔧 Configuration Files

### Edge Configuration (`edge/.env`)
```bash
DEVICE_ID=aicamera-edge-001
DEVICE_MODEL=AI-CAM-EDGE-V2
SERVER_URL=http://localhost:3000
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
SERVER_SFTP_HOST=localhost
SERVER_SFTP_USERNAME=aicamera
SERVER_SFTP_PASSWORD=aicamera123
```

### Server Configuration (`server/.env`)
```bash
DATABASE_URL="postgresql://aicamera:aicamera123@localhost:5432/aicamera_db"
JWT_SECRET=your-super-secret-jwt-key
API_KEY_SECRET=your-api-key-secret
PORT=3000
NODE_ENV=development
```

### Communication Configuration (`server/.env.communication`)
```bash
MQTT_ENABLED=true
MQTT_URL=mqtt://localhost:1883
SFTP_ENABLED=true
SFTP_PORT=2222
SFTP_PASSWORD=aicamera123
IMAGE_STORAGE_PATH=./image_storage
```

## 🐛 Troubleshooting

### Common Issues

#### Python Issues
```bash
# If pip install fails
pip install --upgrade pip setuptools wheel

# If OpenCV installation fails (Windows)
# Download pre-built wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/

# If virtual environment issues
python3 -m venv --clear venv
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Database Issues
```bash
# Reset PostgreSQL
sudo -u postgres dropdb aicamera_db
sudo -u postgres createdb aicamera_db

# Reset Prisma
npx prisma migrate reset
npx prisma db push
```

#### Communication Issues
```bash
# Check MQTT broker
sudo systemctl status mosquitto
sudo systemctl restart mosquitto

# Check SSH/SFTP
sudo systemctl status ssh
sudo systemctl restart ssh

# Check ports
netstat -tulpn | grep :1883  # MQTT
netstat -tulpn | grep :22    # SSH
netstat -tulpn | grep :3000  # Server
```

## 📚 Development Workflow

### Daily Commands
```bash
# Start development environment
./scripts/start_dev.sh

# Run tests
./scripts/run_tests.sh

# Format code
./scripts/format_code.sh

# Lint code
./scripts/lint_code.sh
```

### Useful Commands
```bash
# Edge development
cd edge
source venv/bin/activate
python -m pytest tests/ -v
python scripts/edge_device_simulator.py

# Server development
cd server
npm run start:dev
npm run test:watch
npx prisma studio

# Database operations
npx prisma migrate dev
npx prisma db seed
npx prisma generate

# Communication testing
python scripts/test_communication_system.py
```

## 🔒 Security Notes

### Production Deployment
- Change all default passwords
- Use strong JWT secrets
- Enable TLS/SSL for all communication
- Configure firewall rules
- Use environment-specific configurations

### Development Security
- Default credentials are for development only
- Never commit `.env` files to version control
- Use `.env.example` files for templates
- Regularly update dependencies

## 📖 Additional Resources

### Documentation
- [Development Setup Guide](DEVELOPMENT_SETUP_GUIDE.md)
- [Communication System Implementation](COMMUNICATION_SYSTEM_IMPLEMENTATION.md)
- [API Documentation](http://localhost:3000/api)

### Tools
- [VS Code](https://code.visualstudio.com/)
- [Postman](https://www.postman.com/) - API testing
- [DBeaver](https://dbeaver.io/) - Database management
- [MQTT Explorer](http://mqtt-explorer.com/) - MQTT client

### Learning Resources
- [Python for AI/ML](https://realpython.com/python-machine-learning/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [NestJS Tutorial](https://docs.nestjs.com/first-steps)
- [Vue.js Tutorial](https://vuejs.org/tutorial/)

## ✅ Verification Checklist

- [ ] Git installed and configured
- [ ] Python 3.9+ installed with virtual environment
- [ ] Node.js 16+ installed with npm/yarn
- [ ] PostgreSQL installed and running
- [ ] SQLite available
- [ ] MQTT broker (Mosquitto) installed and running
- [ ] SSH/SFTP server configured
- [ ] Project cloned and dependencies installed
- [ ] Environment files configured
- [ ] Databases initialized
- [ ] All services starting successfully
- [ ] Communication system tested
- [ ] Development workflow working

## 🎉 Congratulations!

Your development machine is now fully configured for AI Camera monorepo development! You can:

1. **Develop Edge Components** in Python with AI/ML capabilities
2. **Develop Server Components** in Node.js with NestJS
3. **Test Communication** between edge and server
4. **Manage Databases** for both edge and server
5. **Use Modern Development Tools** for efficient coding

Start by running the edge simulator and testing the complete communication workflow. Happy coding! 🚀

---

**Need Help?**
- Check the troubleshooting section above
- Review the detailed setup guide
- Check the communication system documentation
- Open an issue in the project repository
