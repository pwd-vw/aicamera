# AI Camera Development Environment Setup Script for Windows
# This script automates the setup of the development environment for the AI Camera monorepo on Windows

param(
    [switch]$SkipChocolatey,
    [switch]$SkipDocker,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to install Chocolatey
function Install-Chocolatey {
    Write-Status "Installing Chocolatey package manager..."
    
    if (Test-Command "choco") {
        Write-Success "Chocolatey already installed"
        return
    }
    
    if (-not (Test-Administrator)) {
        Write-Error "Please run this script as Administrator to install Chocolatey"
        exit 1
    }
    
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    Write-Success "Chocolatey installed successfully"
}

# Function to install system dependencies
function Install-SystemDependencies {
    Write-Status "Installing system dependencies..."
    
    if (-not $SkipChocolatey) {
        Install-Chocolatey
    }
    
    $packages = @(
        "git",
        "python",
        "nodejs",
        "postgresql",
        "visualstudio2019buildtools",
        "visualstudio2019-workload-vctools"
    )
    
    foreach ($package in $packages) {
        if (-not (Test-Command $package)) {
            Write-Status "Installing $package..."
            choco install $package -y
        } else {
            Write-Status "$package already installed"
        }
    }
    
    # Install Docker Desktop if not skipped
    if (-not $SkipDocker) {
        if (-not (Test-Command "docker")) {
            Write-Status "Installing Docker Desktop..."
            choco install docker-desktop -y
        } else {
            Write-Status "Docker already installed"
        }
    }
    
    Write-Success "System dependencies installed"
}

# Function to setup Python environment
function Setup-PythonEnvironment {
    Write-Status "Setting up Python environment..."
    
    # Check if Python is installed
    if (-not (Test-Command "python")) {
        Write-Error "Python not found. Please install Python 3.9+ first."
        exit 1
    }
    
    # Navigate to edge directory
    Push-Location "edge"
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path "venv")) {
        Write-Status "Creating Python virtual environment..."
        python -m venv venv
    } else {
        Write-Status "Virtual environment already exists"
    }
    
    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & "venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    if (Test-Path "requirements.txt") {
        Write-Status "Installing Python dependencies..."
        pip install -r requirements.txt
    }
    
    # Install additional communication dependencies
    $pythonPackages = @(
        "paho-mqtt",
        "paramiko",
        "python-socketio",
        "requests",
        "pillow",
        "opencv-python",
        "numpy",
        "pytest",
        "pytest-cov",
        "black",
        "flake8",
        "mypy",
        "pre-commit"
    )
    
    foreach ($package in $pythonPackages) {
        Write-Status "Installing $package..."
        pip install $package
    }
    
    Pop-Location
    Write-Success "Python environment setup complete"
}

# Function to setup Node.js environment
function Setup-NodeJSEnvironment {
    Write-Status "Setting up Node.js environment..."
    
    # Check if Node.js is installed
    if (-not (Test-Command "node")) {
        Write-Error "Node.js not found. Please install Node.js LTS first."
        exit 1
    }
    
    # Navigate to server directory
    Push-Location "server"
    
    # Install dependencies
    if (Test-Path "package.json") {
        Write-Status "Installing Node.js dependencies..."
        npm install
        
        # Install additional communication dependencies
        $npmPackages = @(
            "mqtt",
            "ssh2",
            "ssh2-sftp-client",
            "socket.io",
            "@nestjs/websockets",
            "@nestjs/platform-socket.io"
        )
        
        foreach ($package in $npmPackages) {
            Write-Status "Installing $package..."
            npm install $package
        }
        
        # Install development dependencies
        $devPackages = @(
            "@types/node",
            "@types/jest",
            "jest",
            "ts-jest",
            "@nestjs/testing",
            "supertest",
            "@types/supertest"
        )
        
        foreach ($package in $devPackages) {
            Write-Status "Installing dev dependency $package..."
            npm install -D $package
        }
    }
    
    Pop-Location
    Write-Success "Node.js environment setup complete"
}

# Function to setup frontend environment
function Setup-FrontendEnvironment {
    Write-Status "Setting up frontend environment..."
    
    if (Test-Path "frontend") {
        Push-Location "frontend"
        
        if (Test-Path "package.json") {
            Write-Status "Installing frontend dependencies..."
            npm install
        }
        
        Pop-Location
        Write-Success "Frontend environment setup complete"
    } else {
        Write-Warning "Frontend directory not found, skipping"
    }
}

# Function to setup PostgreSQL
function Setup-PostgreSQL {
    Write-Status "Setting up PostgreSQL..."
    
    # Check if PostgreSQL is installed
    if (-not (Test-Command "psql")) {
        Write-Error "PostgreSQL not found. Please install PostgreSQL first."
        exit 1
    }
    
    # Create database user and database
    try {
        Write-Status "Creating database user and database..."
        
        # Note: This requires PostgreSQL to be running and accessible
        # You may need to manually create the user and database
        Write-Warning "Please manually create PostgreSQL user and database:"
        Write-Warning "1. Open pgAdmin or psql"
        Write-Warning "2. Create user: CREATE USER aicamera WITH PASSWORD 'aicamera123';"
        Write-Warning "3. Create database: CREATE DATABASE aicamera_db OWNER aicamera;"
        Write-Warning "4. Grant privileges: GRANT ALL PRIVILEGES ON DATABASE aicamera_db TO aicamera;"
        
    } catch {
        Write-Warning "Could not setup PostgreSQL automatically. Please setup manually."
    }
    
    Write-Success "PostgreSQL setup instructions provided"
}

# Function to setup databases
function Setup-Databases {
    Write-Status "Setting up databases..."
    
    # Setup PostgreSQL
    Setup-PostgreSQL
    
    # Setup server database
    Push-Location "server"
    if (Test-Command "npx") {
        Write-Status "Setting up Prisma..."
        npx prisma generate
        npx prisma db push --preview-feature
    }
    Pop-Location
    
    # Setup edge database
    Push-Location "edge"
    if (Test-Path "scripts\init_database.py") {
        Write-Status "Initializing edge database..."
        & "venv\Scripts\python.exe" scripts\init_database.py
    }
    Pop-Location
    
    Write-Success "Databases setup complete"
}

# Function to create environment files
function Create-EnvironmentFiles {
    Write-Status "Creating environment files..."
    
    # Edge environment
    if (-not (Test-Path "edge\.env")) {
        Write-Status "Creating edge environment file..."
        @"
# Device Configuration
DEVICE_ID=aicamera-edge-001
DEVICE_MODEL=AI-CAM-EDGE-V2
SERVER_URL=http://localhost:3000

# Communication Settings
MQTT_ENABLED=true
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

# SFTP Settings
SERVER_SFTP_HOST=localhost
SERVER_SFTP_PORT=22
SERVER_SFTP_USERNAME=aicamera
SERVER_SFTP_PASSWORD=aicamera123

# Storage Settings
STORAGE_MANAGER_ENABLED=true
IMAGE_COMPRESSION_ENABLED=true
IMAGE_COMPRESSION_QUALITY=85
"@ | Out-File -FilePath "edge\.env" -Encoding UTF8
        Write-Success "Edge environment file created"
    }
    
    # Server environment
    if (-not (Test-Path "server\.env")) {
        Write-Status "Creating server environment file..."
        @"
# Database Configuration
DATABASE_URL="postgresql://aicamera:aicamera123@localhost:5432/aicamera_db"

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
API_KEY_SECRET=your-api-key-secret-change-this-in-production

# Server Configuration
PORT=3000
NODE_ENV=development
"@ | Out-File -FilePath "server\.env" -Encoding UTF8
        Write-Success "Server environment file created"
    }
    
    # Communication environment
    if (-not (Test-Path "server\.env.communication")) {
        Write-Status "Creating communication environment file..."
        @"
# MQTT Broker Settings
MQTT_ENABLED=true
MQTT_URL=mqtt://localhost:1883

# SFTP Server Settings
SFTP_ENABLED=true
SFTP_PORT=2222
SFTP_PASSWORD=aicamera123

# Image Storage Settings
IMAGE_STORAGE_PATH=./image_storage
IMAGE_THUMBNAIL_SIZE=200
"@ | Out-File -FilePath "server\.env.communication" -Encoding UTF8
        Write-Success "Communication environment file created"
    }
}

# Function to create directories
function Create-Directories {
    Write-Status "Creating necessary directories..."
    
    $directories = @(
        "server\image_storage",
        "edge\captured_images",
        "logs"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Status "Created directory: $dir"
        }
    }
    
    Write-Success "Directories created"
}

# Function to verify installation
function Verify-Installation {
    Write-Status "Verifying installation..."
    
    $checks = @(
        @{ Command = "python"; Name = "Python" },
        @{ Command = "node"; Name = "Node.js" },
        @{ Command = "npm"; Name = "npm" },
        @{ Command = "git"; Name = "Git" },
        @{ Command = "psql"; Name = "PostgreSQL" }
    )
    
    foreach ($check in $checks) {
        if (Test-Command $check.Command) {
            $version = & $check.Command --version 2>$null
            Write-Success "$($check.Name): $version"
        } else {
            Write-Error "$($check.Name) not found"
        }
    }
    
    # Check Docker
    if (Test-Command "docker") {
        $version = docker --version
        Write-Success "Docker: $version"
    } else {
        Write-Warning "Docker not found (optional)"
    }
    
    Write-Success "Installation verification complete"
}

# Function to provide next steps
function Show-NextSteps {
    Write-Success "🎉 Development environment setup complete!"
    Write-Host ""
    Write-Status "Next steps:"
    Write-Status "1. Start the server: cd server && npm run start:dev"
    Write-Status "2. Start the frontend: cd frontend && npm run serve"
    Write-Status "3. Run edge simulator: cd edge\scripts && .\run_simulator.ps1"
    Write-Status "4. Access admin dashboard: http://localhost:8080"
    Write-Status "5. Monitor MQTT: Use MQTT Explorer or similar tool"
    Write-Host ""
    Write-Status "Happy coding! 🚀"
}

# Main setup function
function Main {
    Write-Status "Starting AI Camera development environment setup for Windows..."
    
    # Check if running as administrator (for some operations)
    if (-not (Test-Administrator)) {
        Write-Warning "Some operations may require Administrator privileges"
    }
    
    # Install system dependencies
    Install-SystemDependencies
    
    # Setup Python environment
    Setup-PythonEnvironment
    
    # Setup Node.js environment
    Setup-NodeJSEnvironment
    
    # Setup frontend environment
    Setup-FrontendEnvironment
    
    # Setup databases
    Setup-Databases
    
    # Create environment files
    Create-EnvironmentFiles
    
    # Create directories
    Create-Directories
    
    # Verify installation
    Verify-Installation
    
    # Show next steps
    Show-NextSteps
}

# Run main function
Main
