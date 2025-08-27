# AI Camera Development Machine Setup Guide

## 🎯 Overview

This guide will help you set up your development machine to work with the AI Camera monorepo, which includes:
- **Edge Components**: Python-based camera and AI processing
- **Server Components**: Node.js with NestJS backend
- **Communication System**: MQTT, SFTP, WebSocket, REST API
- **Database**: PostgreSQL (server) and SQLite (edge)
- **Frontend**: Vue.js admin dashboard

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+ recommended)
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: At least 10GB free space
- **Network**: Internet connection for package downloads

### Required Software

## 🛠️ Step 1: Install Core Development Tools

### 1.1 Git Version Control
```bash
# Windows (using Chocolatey)
choco install git

# macOS (using Homebrew)
brew install git

# Ubuntu/Debian
sudo apt update
sudo apt install git

# Verify installation
git --version
```

### 1.2 Code Editor/IDE
```bash
# Install Visual Studio Code (recommended)
# Download from: https://code.visualstudio.com/

# Or install via package manager
# Windows
choco install vscode

# macOS
brew install --cask visual-studio-code

# Ubuntu
sudo snap install code --classic
```

### 1.3 Terminal/Shell
```bash
# Windows: Use Windows Terminal (recommended)
# Install from Microsoft Store or:
choco install microsoft-windows-terminal

# macOS: Use iTerm2
brew install --cask iterm2

# Ubuntu: Use default terminal or install Terminator
sudo apt install terminator
```

## 🐍 Step 2: Install Python Environment (Edge Development)

### 2.1 Install Python
```bash
# Windows
# Download from: https://www.python.org/downloads/
# Or using Chocolatey:
choco install python

# macOS
brew install python

# Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

### 2.2 Install Python Virtual Environment Tools
```bash
# Install virtualenv and pip-tools
pip3 install virtualenv pip-tools

# Or using system package manager
# Ubuntu
sudo apt install python3-venv python3-pip-tools
```

### 2.3 Install Python Development Libraries
```bash
# Ubuntu/Debian (system dependencies for Python packages)
sudo apt install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    pkg-config \
    libpq-dev \
    libsqlite3-dev

# macOS
brew install \
    openssl \
    libffi \
    pkg-config \
    postgresql \
    sqlite3

# Windows
# Install Visual Studio Build Tools for C++ extensions
# Download from: https://visualstudio.microsoft.com/downloads/
```

## 🟢 Step 3: Install Node.js Environment (Server Development)

### 3.1 Install Node.js
```bash
# Using Node Version Manager (nvm) - Recommended
# Windows: nvm-windows
# Download from: https://github.com/coreybutler/nvm-windows/releases

# macOS/Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc  # or ~/.zshrc

# Install Node.js LTS
nvm install --lts
nvm use --lts

# Verify installation
node --version
npm --version
```

### 3.2 Install Node.js Package Managers
```bash
# Install yarn (optional but recommended)
npm install -g yarn

# Install pnpm (alternative to npm)
npm install -g pnpm

# Verify installations
yarn --version
pnpm --version
```

## 🗄️ Step 4: Install Database Systems

### 4.1 Install PostgreSQL (Server Database)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew install postgresql@14
brew services start postgresql@14

# Windows
# Download from: https://www.postgresql.org/download/windows/
# Or using Chocolatey:
choco install postgresql

# Create database user
sudo -u postgres createuser --interactive
# Enter username: aicamera
# Enter password: aicamera123
# Superuser? No
# Create databases? No
# Create more new roles? No

# Create database
sudo -u postgres createdb aicamera_db
```

### 4.2 Install SQLite (Edge Database)
```bash
# Ubuntu/Debian
sudo apt install sqlite3 libsqlite3-dev

# macOS
brew install sqlite3

# Windows
# Usually comes with Python, or download from: https://www.sqlite.org/download.html

# Verify installation
sqlite3 --version
```

## 🔧 Step 5: Install Communication System Dependencies

### 5.1 Install MQTT Broker (Mosquitto)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mosquitto mosquitto-clients

# Start and enable Mosquitto
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# macOS
brew install mosquitto
brew services start mosquitto

# Windows
# Download from: https://mosquitto.org/download/
# Or using Chocolatey:
choco install mosquitto
```

### 5.2 Install SSH/SFTP Server
```bash
# Ubuntu/Debian
sudo apt install openssh-server

# Start and enable SSH
sudo systemctl start ssh
sudo systemctl enable ssh

# macOS
# SSH server is usually pre-installed
sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist

# Windows
# Enable OpenSSH Server in Windows Features
# Or install via PowerShell:
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
```

### 5.3 Install Rsync
```bash
# Ubuntu/Debian
sudo apt install rsync

# macOS
# Usually pre-installed

# Windows
# Install via WSL or Git Bash (comes with Git for Windows)
# Or using Chocolatey:
choco install rsync
```

## 🐳 Step 6: Install Container Tools (Optional but Recommended)

### 6.1 Install Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# macOS
brew install --cask docker

# Windows
# Download Docker Desktop from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

## 📦 Step 7: Install Project Dependencies

### 7.1 Clone the Repository
```bash
# Clone the monorepo
git clone <your-repository-url> aicamera
cd aicamera

# Or if you already have the code
cd /path/to/your/aicamera
```

### 7.2 Setup Python Environment (Edge)
```bash
# Navigate to edge directory
cd edge

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional communication dependencies
pip install \
    paho-mqtt \
    paramiko \
    python-socketio \
    requests \
    pillow \
    opencv-python \
    numpy \
    sqlite3

# Install development dependencies
pip install \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    pre-commit
```

### 7.3 Setup Node.js Environment (Server)
```bash
# Navigate to server directory
cd ../server

# Install dependencies
npm install

# Or using yarn
yarn install

# Install additional communication dependencies
npm install \
    mqtt \
    ssh2 \
    ssh2-sftp-client \
    socket.io \
    @nestjs/websockets \
    @nestjs/platform-socket.io

# Install development dependencies
npm install -D \
    @types/node \
    @types/jest \
    jest \
    ts-jest \
    @nestjs/testing \
    supertest \
    @types/supertest
```

### 7.4 Setup Frontend Environment
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Or using yarn
yarn install
```

## ⚙️ Step 8: Configure Development Environment

### 8.1 Create Environment Files
```bash
# Create edge environment file
cd edge
cp .env.example .env

# Edit edge environment
nano .env
# Add your configuration:
# DEVICE_ID=aicamera-edge-001
# DEVICE_MODEL=AI-CAM-EDGE-V2
# SERVER_URL=http://localhost:3000
# MQTT_BROKER_HOST=localhost
# MQTT_BROKER_PORT=1883
# SERVER_SFTP_HOST=localhost
# SERVER_SFTP_PORT=22
# SERVER_SFTP_USERNAME=aicamera
# SERVER_SFTP_PASSWORD=aicamera123

# Create server environment file
cd ../server
cp .env.example .env

# Edit server environment
nano .env
# Add your configuration:
# DATABASE_URL="postgresql://aicamera:aicamera123@localhost:5432/aicamera_db"
# JWT_SECRET=your-super-secret-jwt-key
# API_KEY_SECRET=your-api-key-secret

# Create communication environment file
cp .env.communication.example .env.communication

# Edit communication environment
nano .env.communication
# Add your configuration:
# MQTT_ENABLED=true
# MQTT_URL=mqtt://localhost:1883
# SFTP_ENABLED=true
# SFTP_PORT=2222
# SFTP_PASSWORD=aicamera123
# IMAGE_STORAGE_PATH=./image_storage
```

### 8.2 Setup Database
```bash
# Navigate to server directory
cd server

# Run database migrations
npx prisma migrate dev

# Generate Prisma client
npx prisma generate

# Seed database (if applicable)
npx prisma db seed
```

### 8.3 Initialize Edge Database
```bash
# Navigate to edge directory
cd ../edge

# Run database initialization script
python scripts/init_database.py
```

## 🚀 Step 9: Setup Development Tools

### 9.1 Install VS Code Extensions
```bash
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-vscode.vscode-json
code --install-extension ms-vscode.vscode-yaml
code --install-extension redhat.vscode-yaml
code --install-extension ms-vscode.vscode-docker
code --install-extension ms-vscode.vscode-git
code --install-extension eamodio.gitlens
code --install-extension ms-vscode.vscode-eslint
code --install-extension ms-vscode.vscode-prettier
code --install-extension streetsidesoftware.code-spell-checker
```

### 9.2 Setup Git Hooks
```bash
# Navigate to project root
cd ..

# Install pre-commit hooks
pre-commit install

# Or manually setup
mkdir -p .git/hooks
cp scripts/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### 9.3 Setup Development Scripts
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x edge/scripts/*.sh
chmod +x server/scripts/*.sh
```

## 🧪 Step 10: Verify Installation

### 10.1 Test Python Environment
```bash
# Navigate to edge directory
cd edge

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Test Python packages
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
python -c "import numpy; print('NumPy version:', numpy.__version__)"
python -c "import paho.mqtt.client; print('MQTT client available')"
python -c "import paramiko; print('Paramiko available')"

# Run edge tests
python -m pytest tests/
```

### 10.2 Test Node.js Environment
```bash
# Navigate to server directory
cd ../server

# Test Node.js packages
node -e "console.log('Node.js version:', process.version)"
npm test

# Test database connection
npx prisma db push --preview-feature
```

### 10.3 Test Communication System
```bash
# Start MQTT broker (if not running)
sudo systemctl start mosquitto

# Test MQTT
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test

# Test SFTP
sftp aicamera@localhost

# Test PostgreSQL
psql -h localhost -U aicamera -d aicamera_db -c "SELECT version();"
```

## 🎯 Step 11: Start Development

### 11.1 Start All Services
```bash
# Terminal 1: Start Server
cd server
npm run start:dev

# Terminal 2: Start Frontend
cd frontend
npm run serve

# Terminal 3: Start Edge Simulator
cd edge/scripts
./run_simulator.sh

# Terminal 4: Monitor Communication
mosquitto_sub -h localhost -t "aicamera/#"
```

### 11.2 Access Development Interfaces
- **Server API**: http://localhost:3000
- **Frontend Dashboard**: http://localhost:8080
- **API Documentation**: http://localhost:3000/api
- **Database Admin**: http://localhost:3000/prisma-studio

## 📚 Step 12: Development Workflow

### 12.1 Daily Development Commands
```bash
# Start development environment
./scripts/start_dev.sh

# Run tests
./scripts/run_tests.sh

# Format code
./scripts/format_code.sh

# Lint code
./scripts/lint_code.sh

# Build for production
./scripts/build.sh
```

### 12.2 Useful Development Commands
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

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Python Issues
```bash
# If pip install fails on Windows
pip install --upgrade pip setuptools wheel

# If OpenCV installation fails
# Windows: Download pre-built wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/
# Linux: Install system dependencies first
sudo apt install python3-opencv

# If virtual environment issues
python3 -m venv --clear venv
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall node_modules
rm -rf node_modules package-lock.json
npm install

# If Prisma issues
npx prisma generate
npx prisma db push
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

## 📖 Additional Resources

### Documentation
- [Python Documentation](https://docs.python.org/)
- [Node.js Documentation](https://nodejs.org/docs/)
- [NestJS Documentation](https://docs.nestjs.com/)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [Vue.js Documentation](https://vuejs.org/guide/)

### Development Tools
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
- [ ] Python 3.8+ installed with virtual environment
- [ ] Node.js 16+ installed with npm/yarn
- [ ] PostgreSQL installed and running
- [ ] SQLite available
- [ ] MQTT broker (Mosquitto) installed and running
- [ ] SSH/SFTP server configured
- [ ] Rsync available
- [ ] Docker installed (optional)
- [ ] VS Code with extensions
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
