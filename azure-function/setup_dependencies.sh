#!/bin/bash

# Create virtual environment if it doesn't exist
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt --target=".python_packages/lib/site-packages"

# Deactivate virtual environment
deactivate

echo "Dependencies installed successfully to .python_packages/lib/site-packages"