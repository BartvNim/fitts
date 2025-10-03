#!/bin/bash
# Setup script for libpointing_example
# This script automates the setup process described in README.md

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    libpointing Example - Automated Setup                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "libpointing_demo.py" ]; then
    echo "❌ Error: Please run this script from the libpointing_example directory"
    exit 1
fi

# Step 1: Check for Homebrew and libpointing
echo "📦 Checking prerequisites..."
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install it first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

if ! brew list libpointing &> /dev/null; then
    echo "⚠️  libpointing not installed. Installing via Homebrew..."
    brew install libpointing
else
    echo "✅ libpointing is installed"
fi

# Step 2: Clone libpointing if not present
if [ ! -d "libpointing" ]; then
    echo ""
    echo "📥 Cloning libpointing library..."
    git clone https://github.com/INRIA/libpointing.git
    echo "✅ libpointing cloned"
else
    echo "✅ libpointing directory exists"
fi

# Step 3: Setup virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "🐍 Creating virtual environment..."
    python3.12 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Step 4: Install Python dependencies
echo ""
echo "📦 Installing Python dependencies (including Cython and setuptools)..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ All dependencies installed"

# Step 5: Copy helper files
echo ""
echo "📋 Copying helper files..."
cp __init__.py libpointing/bindings/Python/cython/libpointing/__init__.py
echo "✅ Copied fixed __init__.py"

cp build_homebrew.py libpointing/bindings/Python/cython/build_homebrew.py
echo "✅ Copied build_homebrew.py"

# Step 6: Build Python bindings
echo ""
echo "🔨 Building libpointing Python bindings..."
cd libpointing/bindings/Python/cython
python build_homebrew.py build_ext --inplace
cd ../../../..

# Step 7: Verify installation
echo ""
echo "🧪 Verifying installation..."
if python -c "import sys; sys.path.insert(0, 'libpointing/bindings/Python/cython'); from libpointing.libpointing import PointingDevice" 2>/dev/null; then
    echo "✅ Python bindings loaded successfully!"
else
    echo "❌ Failed to load Python bindings"
    exit 1
fi

# Done!
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 ✨ Setup Complete! ✨                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 You can now run the demo:"
echo "   source venv/bin/activate"
echo "   python libpointing_demo.py"
echo ""
echo "📖 For more information, see README.md"
echo ""
