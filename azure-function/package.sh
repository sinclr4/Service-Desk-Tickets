#!/bin/bash

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Copy function app files to temp directory
cp -r * $TEMP_DIR/
cd $TEMP_DIR

# Remove unnecessary files
rm -rf .venv __pycache__ .git .github

# Create virtual environment
python -m venv .env
source .env/bin/activate

# Create the destination directory for packages
mkdir -p .python_packages/lib/site-packages

# Install dependencies
pip install -r requirements.txt --target=.python_packages/lib/site-packages

# Deactivate virtual environment
deactivate

# Create the deployment zip
zip -r ../function-app.zip .

# Return to original directory
cd -
echo "Deployment package created at function-app.zip"