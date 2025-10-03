# libpointing Raw HID Mouse Demo

A Python demonstration application that uses the [libpointing](http://libpointing.org/) library to capture raw HID (Human Interface Device) events directly from pointing devices, bypassing the operating system's transfer functions.

## Quick Start

### Windows (Recommended - Simplest Setup!)

**⚠️ IMPORTANT:** Requires Python 3.11 / 3.12 (not 3.13+)

```powershell
# Clone the repository
git clone https://github.com/yourusername/libpointing_example.git
cd libpointing_example

# Run the automated setup script (will automatically use Python 3.11 / 3.12)
.\setup_windows.ps1

# Run the demo
.\venv\Scripts\Activate.ps1
python libpointing_demo.py
```

**Note:** On Windows, libpointing uses precompiled binaries from PyPI. No compilation needed!

### macOS (Automated Setup)

```bash
# Clone the repository
git clone https://github.com/yourusername/libpointing_example.git
cd libpointing_example

# Run the automated setup script
./setup.sh

# Run the demo
source venv/bin/activate
python libpointing_demo.py
```

### Manual Setup

#### Windows

**⚠️ IMPORTANT:** Requires Python 3.11 / 3.12 (not 3.13+)

```powershell
# Clone and setup
git clone https://github.com/yourusername/libpointing_example.git
cd libpointing_example

# Install dependencies (libpointing comes precompiled from PyPI!)
# Use py -3.12 to specify the correct Python version
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the demo
python libpointing_demo.py
```

**That's it!** On Windows, the PyPI package includes precompiled binaries. No building required.

#### macOS

```bash
# Clone and setup
git clone https://github.com/yourusername/libpointing_example.git
cd libpointing_example
git clone https://github.com/INRIA/libpointing.git

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Fix libpointing bindings
cp __init__.py libpointing/bindings/Python/cython/libpointing/__init__.py
cp build_homebrew.py libpointing/bindings/Python/cython/build_homebrew.py

# Build Python bindings
cd libpointing/bindings/Python/cython
python build_homebrew.py build_ext --inplace
cd ../../../..

# Run the demo
python libpointing_demo.py
```

## Overview

This demo showcases how to:
- Access raw HID events directly from pointing devices
- Retrieve actual device parameters (resolution, update frequency)
- Display raw counts from the device (not pixels)
- Bypass OS pointer acceleration and transfer functions
- Work with libpointing's Python bindings via Cython

## Features

- **Raw HID Access**: Captures mouse events directly from hardware
- **Real Device Metrics**: Shows actual resolution (counts/inch) and update frequency (Hz)
- **Visual Feedback**: Interactive pygame window with crosshair pointer
- **Device Information**: Displays vendor, product, VID:PID, and URI information
- **Configurable**: JSON configuration for device selection and display settings

## Prerequisites

### Windows

1. **Python 3.11 or 3.12** with pip ⚠️ **IMPORTANT**
   - Download from [python.org](https://www.python.org/downloads/)
   - **libpointing on PyPI only supports Python 3.11 and 3.12**
   - Python 3.13+ is **NOT** supported yet
   - Make sure to check "Add Python to PATH" during installation

2. **libpointing** (precompiled via PyPI)
   - Automatically installed with `pip install libpointing`
   - No additional dependencies needed!

### macOS

1. **libpointing** (via Homebrew):
   ```bash
   brew install libpointing
   ```

2. **Python 3.8+** with pip

3. **Xcode Command Line Tools** (for building Python bindings):
   ```bash
   xcode-select --install
   ```

## Installation

### Windows Installation

#### Step 1: Clone the Repository

```powershell
git clone https://github.com/yourusername/libpointing_example.git
cd libpointing_example
```

#### Step 2: Set Up Python Virtual Environment

**⚠️ IMPORTANT:** Use Python 3.11 or 3.12 (not 3.13+)

```powershell
# Use Python 3.11 or 3.12
py -3.12 -m venv venv
# or: py -3.11 -m venv venv

.\venv\Scripts\Activate.ps1
```

#### Step 3: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

**That's it!** The `libpointing` package from PyPI includes precompiled Windows binaries. No building or compilation required!

#### Step 4: Run the example

```powershell
python libpointing_demo.py
```

### macOS Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/libpointing_example.git
cd libpointing_example
```

### Step 2: Clone the libpointing Library

The libpointing library needs to be cloned as a submodule or directly:

```bash
git clone https://github.com/INRIA/libpointing.git
```

### Step 3: Set Up Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Fix the libpointing Python Bindings for macOS

The original libpointing bindings need two modifications to work properly on macOS:

#### 5a. Fix the `__init__.py` file

The original `__init__.py` tries to import Windows-specific modules on all platforms. Replace it with the fixed version:

```bash
cp __init__.py libpointing/bindings/Python/cython/libpointing/__init__.py
```

Or manually edit `libpointing/bindings/Python/cython/libpointing/__init__.py` to wrap the Windows import in a platform check:

```python
import platform

from .libpointing import (
    PointingDevice,
    DisplayDevice,
    TransferFunction,
    PointingDeviceManager,
    PointingDeviceDescriptor,
    )

# Windows-specific acceleration function
if platform.system() == 'Windows':
    from .libpointing import winSystemPointerAcceleration
```

#### 5b. Add the Homebrew build script

Copy the `build_homebrew.py` script into the bindings directory:

```bash
cp build_homebrew.py libpointing/bindings/Python/cython/build_homebrew.py
```

This script is configured to use the Homebrew-installed libpointing library.

### Step 6: Build the libpointing Python Bindings

```bash
cd libpointing/bindings/Python/cython
./venv/bin/python build_homebrew.py build_ext --inplace
cd ../../../..
```

### Step 7: Verify the Installation

```bash
python -c "import sys; sys.path.insert(0, 'libpointing/bindings/Python/cython'); from libpointing.libpointing import PointingDevice; print('✓ Bindings loaded successfully!')"
```

Or with explicit Python path:

```bash
./venv/bin/python -c "import sys; sys.path.insert(0, 'libpointing/bindings/Python/cython'); from libpointing.libpointing import PointingDevice; print('✓ Bindings loaded successfully!')"
```

## Configuration

Edit `config.json` to configure your device and display settings:

```json
{
  "device": {
    "uri": "any:?vendor=0x46d&product=0xb034&cpi=2000&hz=125&debugLevel=2",
    "description": "MX Master 3S Bluetooth"
  },
  "display": {
    "width": 1200,
    "height": 800,
    "target_size": 25,
    "background_color": [20, 20, 25],
    "target_color": [100, 200, 255],
    "text_color": [220, 220, 220]
  }
}
```

### Device URI Options

The device URI supports several formats:

- `any:` - Use any available pointing device
- `usb:` - Use any USB pointing device
- `usb:046d:c52b` - Specific device by VID:PID
- `any:?vendor=0x46d&product=0xb034&cpi=2000&hz=125` - Device with parameters

Parameters:
- `vendor` - Vendor ID (hex)
- `product` - Product ID (hex)
- `cpi` - Counts per inch (resolution)
- `hz` - Update frequency
- `debugLevel` - Debug verbosity (0-3)

## Usage

### Windows

1. **Activate the virtual environment** (if not already active):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Run the demo**:
   ```powershell
   python libpointing_demo.py
   ```

3. **Controls**:
   - Move your mouse to see raw HID data
   - `R` - Reset pointer position to center
   - `ESC` or `Q` - Quit application

### macOS

1. **Activate the virtual environment** (if not already active):
   ```bash
   source venv/bin/activate
   ```

2. **Run the demo**:
   ```bash
   ./venv/bin/python libpointing_demo.py
   ```

3. **Controls**:
   - Move your mouse to see raw HID data
   - `R` - Reset pointer position to center
   - `ESC` or `Q` - Quit application

## What You'll See

The demo window displays:

### Device Information
- Vendor and Product names
- Device URI
- Vendor ID and Product ID (VID:PID)
- Resolution (counts per inch)
- Update Frequency (Hz)

### Raw HID Data
- Current position in screen coordinates
- Last delta (raw counts from device)
- Total counts accumulated (X and Y)
- Number of events received
- Last event timestamp (microseconds)

## Project Structure

```
libpointing_example/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── config.json               # Configuration file
├── .gitignore                # Git ignore rules
├── setup_windows.ps1         # Automated setup script for Windows
├── setup.sh                  # Automated setup script for macOS
├── libpointing_demo.py       # Main demo application
├── __init__.py               # Fixed __init__.py for libpointing (macOS only)
├── build_homebrew.py         # Build script for Homebrew (macOS only)
├── libpointing/              # libpointing library (macOS only - cloned from GitHub)
│   └── bindings/
│       └── Python/
│           └── cython/       # Python bindings (macOS only)
│               ├── build_homebrew.py  # (copied here during setup)
│               └── libpointing/       # Built Python module
│                   └── __init__.py    # (fixed during setup)
└── venv/                     # Python virtual environment
```

**Note:** On Windows, the `libpointing/` directory is **not needed**. The precompiled library is installed directly via PyPI into the virtual environment.

### Helper Files

The repository includes helper files in the root directory:

- **`setup_windows.ps1`**: Automated setup script for Windows (uses PyPI precompiled binaries)
- **`setup.sh`**: Automated setup script for macOS/Linux (builds from source)
- **`__init__.py`**: Fixed version that properly handles platform-specific imports (macOS only - prevents Windows-only imports on macOS/Linux)
- **`build_homebrew.py`**: Build script configured for Homebrew-installed libpointing on macOS (macOS only)

**Windows users:** Only `setup_windows.ps1` is needed. The PyPI package handles everything else automatically!

**macOS users:** These files need to be copied into the libpointing library during setup (automated by `setup.sh`).

## Troubleshooting

### Windows Issues

**Error: No matching distribution found for libpointing**
- **This usually means you're using Python 3.13 or newer!**
- libpointing on PyPI only supports Python 3.11 and 3.12
- Check your Python version: `python --version`
- Use the correct version: `py -3.11 -m venv venv` or `py -3.12 -m venv venv`
- Delete the old venv folder and recreate it with the correct Python version

**Error: Cannot import libpointing**
- Make sure you activated the virtual environment: `.\venv\Scripts\Activate.ps1`
- Verify installation: `pip list | findstr libpointing`
- Try reinstalling: `pip install --force-reinstall libpointing`

**Error: Permission denied when accessing devices**
- Run PowerShell as Administrator
- Check Windows Device Manager to ensure your mouse is recognized
- Some USB receivers may require specific drivers

**PowerShell execution policy error**
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or run the setup differently: `powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1`

### macOS Issues

#### Setup Issues

**Error: Platform-specific import errors on non-Windows systems**
- Make sure you copied the fixed `__init__.py` file:
  ```bash
  cp __init__.py libpointing/bindings/Python/cython/libpointing/__init__.py
  ```

**Can't find build_homebrew.py in libpointing/bindings/Python/cython/**
- Copy the build script from the root directory:
  ```bash
  cp build_homebrew.py libpointing/bindings/Python/cython/build_homebrew.py
  ```

### Build Issues (macOS only)

**Error: `library 'pointing' not found`**
- Ensure libpointing is installed: `brew list libpointing`
- Verify Homebrew path: `brew --prefix` (should be `/opt/homebrew` on Apple Silicon)

**Error: `ModuleNotFoundError: No module named 'Cython'`**
- Install Cython: `pip install Cython`

**Python version mismatch or alias issues**
- Use the explicit venv Python path:
  ```bash
  ./venv/bin/python build_homebrew.py build_ext --inplace
  ```

### Runtime Issues

**Error: Failed to initialize libpointing device**
- **Windows**: 
  - Check device permissions (you may need to run as Administrator)
  - Try different URI formats: `any:`, `usb:`, or specific VID:PID
  - Verify your device is connected and recognized in Device Manager
  - Some wireless mice may need the USB receiver plugged in
- **macOS**:
  - Check device permissions (you may need to grant input monitoring access in System Preferences)
  - Try different URI formats: `any:`, `usb:`, or specific VID:PID
  - Verify your device is connected and recognized by the system

**Import Error: No module named 'libpointing'**
- **Windows**: Activate venv and reinstall: `pip install libpointing`
- **macOS**: 
  - Ensure you built the Python bindings (see Installation step 4)
  - Check that you're running from the correct directory
  - Verify the virtual environment is activated

### Device Detection

**Windows:**
```powershell
Get-PnpDevice -Class Mouse
```

**macOS:**
```bash
system_profiler SPUSBDataType
```

Or check the demo output - it lists all detected HID devices on startup.

## Understanding Raw HID Data

### Counts vs Pixels
- **Raw Counts**: Hardware sensor readings from the mouse
- **Pixels**: Screen coordinates after OS transfer function
- This demo shows **raw counts** directly from the device

### Resolution (CPI/DPI)
- Counts Per Inch (CPI) or Dots Per Inch (DPI)
- Higher resolution = more counts per physical inch of movement
- Example: 2000 CPI means 2000 counts per inch

### Update Frequency
- How often the device reports position updates
- Measured in Hertz (Hz)
- Common values: 125 Hz, 500 Hz, 1000 Hz

## Technical Details

### libpointing Library
- Provides cross-platform access to pointing devices
- Supports Windows, macOS, and Linux
- Offers raw HID access and transfer function research
- More info: http://libpointing.org/

### Python Bindings
- Built with Cython for performance
- Wraps C++ libpointing API
- Provides Pythonic interface to device events

### Architecture
- **Callback-based**: Device events trigger Python callbacks
- **Thread-safe**: Uses locks for data synchronization
- **Non-blocking**: Uses pygame event loop with libpointing idle()

## Credits

- **libpointing**: Géry Casiez, Nicolas Roussel, and contributors (INRIA)
- **Demo Application**: Built as an example of raw HID access

## License

This demo application is provided as an example. Please refer to the libpointing library for its license terms.

## Further Reading

- [libpointing Official Website](http://libpointing.org/)
- [libpointing GitHub Repository](https://github.com/INRIA/libpointing)
- [Transfer Functions Research](http://ns.inria.fr/mjolnir/TransferFunctions/)

---

**Note**: This demo requires appropriate permissions to access HID devices. On macOS, you may need to grant "Input Monitoring" permissions in System Preferences → Security & Privacy → Privacy.
