#!/usr/bin/env bash
set -e

# Remove any existing .venv directory
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

# Check if Python 3.12 is available
if command -v python3.12 &>/dev/null; then
    echo "Python 3.12 is installed, proceeding with python3.12..."
    python3.12 -m venv .venv || { echo "Error: Failed to create virtual environment with Python 3.12."; exit 1; }
else
    echo "The recommended version of Python to run nidum is Python 3.12."
    echo "However, $(python3 --version) is installed. Proceeding with $(python3 --version)..."
    python3 -m venv .venv || { echo "Error: Failed to create virtual environment with Python 3."; exit 1; }
fi

# Activate the virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating the virtual environment..."
    source .venv/bin/activate
else
    echo "Error: Virtual environment activation script not found. Exiting."
    exit 1
fi

# Upgrade pip and install dependencies
echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip setuptools wheel

# Install the current project in editable mode
if [ -f "setup.py" ]; then
    pip install -e .
else
    echo "Error: setup.py not found in the current directory. Exiting."
    exit 1
fi

echo "Installation completed successfully."
