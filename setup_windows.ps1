# Setup script for libpointing_example on Windows
# This script automates the Windows setup process

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "    libpointing Example - Windows Setup                               " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "libpointing_demo.py")) {
    Write-Host "ERROR: Please run this script from the libpointing_example directory" -ForegroundColor Red
    exit 1
}

# Step 1: Check for Python (3.11 or 3.12 required for libpointing)
Write-Host "Checking for Python..." -ForegroundColor Yellow
Write-Host "NOTE: libpointing requires Python 3.11 or 3.12 (not 3.13+)" -ForegroundColor Yellow
Write-Host ""

# Try to find Python 3.12 first, then 3.11
$pythonCmd = $null
$pythonVersion = $null

# Check for Python 3.12
try {
    $test = py -3.12 --version 2>&1
    if ($test -match "3\.12") {
        $pythonCmd = "py -3.12"
        $pythonVersion = $test
        Write-Host "Found Python 3.12: $pythonVersion" -ForegroundColor Green
    }
} catch { }

# If not found, check for Python 3.11
if (-not $pythonCmd) {
    try {
        $test = py -3.11 --version 2>&1
        if ($test -match "3\.11") {
            $pythonCmd = "py -3.11"
            $pythonVersion = $test
            Write-Host "Found Python 3.11: $pythonVersion" -ForegroundColor Green
        }
    } catch { }
}

# If neither found, exit with error
if (-not $pythonCmd) {
    Write-Host ""
    Write-Host "ERROR: Python 3.11 or 3.12 is required!" -ForegroundColor Red
    Write-Host "libpointing on PyPI only supports Python 3.11 and 3.12." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.11 or 3.12 from python.org" -ForegroundColor Yellow
    Write-Host "Available Python versions on your system:" -ForegroundColor Yellow
    py --list
    exit 1
}

# Step 2: Setup virtual environment with correct Python version
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "Creating virtual environment with $pythonVersion..." -ForegroundColor Yellow
    Invoke-Expression "$pythonCmd -m venv venv"
    Write-Host "Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Step 3: Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null
Write-Host "pip upgraded" -ForegroundColor Green

# Step 4: Install Python dependencies from PyPI
Write-Host ""
Write-Host "Installing Python dependencies from PyPI..." -ForegroundColor Yellow
Write-Host "   (This includes pygame and the precompiled libpointing package)" -ForegroundColor Cyan
pip install -r requirements.txt
Write-Host "All dependencies installed" -ForegroundColor Green

# Step 5: Test libpointing import
Write-Host ""
Write-Host "Testing libpointing import..." -ForegroundColor Yellow
$testScript = @"
try:
    from libpointing.libpointing import PointingDevice
    print('SUCCESS')
except ImportError as e:
    print('FAILED: ' + str(e))
except Exception as e:
    print('ERROR: ' + str(e))
"@

$testResult = python -c $testScript 2>&1 | Out-String

if ($testResult -match "SUCCESS") {
    Write-Host "libpointing imported successfully!" -ForegroundColor Green
} else {
    Write-Host "libpointing import test result: $testResult" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Note: The PyPI package may work at runtime even if the import test shows warnings." -ForegroundColor Cyan
}

# Done!
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "                      Setup Complete!                                  " -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run the demo:" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python libpointing_demo.py" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: On Windows, libpointing uses precompiled binaries from PyPI." -ForegroundColor Yellow
Write-Host "      No compilation is needed!" -ForegroundColor Yellow
Write-Host ""
