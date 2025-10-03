"""
Fixed __init__.py for libpointing Python bindings

This file should be copied to:
libpointing/bindings/Python/cython/libpointing/__init__.py

It fixes the original file by wrapping Windows-specific imports in a platform check,
preventing import errors on macOS and Linux.

Usage:
    cp __init__.py libpointing/bindings/Python/cython/libpointing/__init__.py
"""

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
