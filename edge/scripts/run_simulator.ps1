# AI Camera Edge Device Simulator for Windows
# This script runs the edge device simulator for development and testing

param(
    [switch]$Verbose,
    [string]$DeviceId = "aicamera-edge-001",
    [string]$ServerUrl = "http://localhost:3000"
)

# Set error action preference
$ErrorActionPreference = "Continue"

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

# Function to check if virtual environment exists
function Test-VirtualEnvironment {
    if (-not (Test-Path "venv")) {
        Write-Error "Virtual environment not found. Please run setup script first."
        Write-Status "Run: ..\..\scripts\setup_dev_environment.ps1"
        exit 1
    }
}

# Function to activate virtual environment
function Activate-VirtualEnvironment {
    Write-Status "Activating Python virtual environment..."
    
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
        Write-Success "Virtual environment activated"
    } else {
        Write-Error "Virtual environment activation script not found"
        exit 1
    }
}

# Function to check dependencies
function Test-Dependencies {
    Write-Status "Checking dependencies..."
    
    $dependencies = @(
        "paho-mqtt",
        "paramiko", 
        "python-socketio",
        "requests",
        "pillow",
        "opencv-python",
        "numpy"
    )
    
    foreach ($dep in $dependencies) {
        try {
            python -c "import $dep" 2>$null
            Write-Success "$dep available"
        } catch {
            Write-Warning "$dep not found, installing..."
            pip install $dep
        }
    }
}

# Function to run simulator
function Start-Simulator {
    Write-Status "Starting AI Camera Edge Device Simulator..."
    Write-Status "Device ID: $DeviceId"
    Write-Status "Server URL: $ServerUrl"
    Write-Host ""
    
    # Set environment variables
    $env:DEVICE_ID = $DeviceId
    $env:SERVER_URL = $ServerUrl
    
    # Run the simulator
    if (Test-Path "edge_device_simulator.py") {
        Write-Status "Running edge device simulator..."
        python edge_device_simulator.py
    } else {
        Write-Error "Simulator script not found: edge_device_simulator.py"
        exit 1
    }
}

# Main function
function Main {
    Write-Status "AI Camera Edge Device Simulator for Windows"
    Write-Host ""
    
    # Check if we're in the right directory
    if (-not (Test-Path "edge_device_simulator.py")) {
        Write-Error "Please run this script from the edge/scripts directory"
        Write-Status "Current directory: $(Get-Location)"
        exit 1
    }
    
    # Test virtual environment
    Test-VirtualEnvironment
    
    # Activate virtual environment
    Activate-VirtualEnvironment
    
    # Test dependencies
    Test-Dependencies
    
    # Start simulator
    Start-Simulator
}

# Run main function
Main
