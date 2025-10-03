"""
Build script for libpointing Python bindings on macOS with Homebrew

This file should be copied to:
libpointing/bindings/Python/cython/build_homebrew.py

It configures the build to use libpointing installed via Homebrew.

Prerequisites:
    - libpointing installed via Homebrew: brew install libpointing
    - Cython installed: pip install Cython

Usage:
    cp build_homebrew.py libpointing/bindings/Python/cython/build_homebrew.py
    cd libpointing/bindings/Python/cython
    python build_homebrew.py build_ext --inplace
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import platform

# Use Homebrew installation
brew_prefix = "/opt/homebrew"
libpointing_include = f"{brew_prefix}/include"
libpointing_lib = f"{brew_prefix}/lib"

system = platform.system()

windows = False

if system == 'Darwin':
    ext_modules = [Extension(
                        "libpointing.libpointing",
                        ["libpointing.pyx"],
                        language="c++",
                        libraries=['pointing'],
                        include_dirs=[libpointing_include],
                        library_dirs=[libpointing_lib],
                        extra_compile_args=["-stdlib=libc++", "-mmacosx-version-min=10.10", "-std=c++17"],
                        extra_link_args=["-mmacosx-version-min=10.10", "-framework", "CoreGraphics"]
                        )]
else:
    raise NotImplementedError(f"Platform {system} not configured yet. Please use macOS with Homebrew libpointing.")

setup(
    name='libpointing',
    ext_modules = cythonize(ext_modules, compiler_directives={'language_level' : "3"}, compile_time_env={'WINDOWS': windows})
)
