#!/bin/bash

# Script to manually deploy an Azure Function App
# Prerequisites: Azure CLI installed and logged in

# Configuration
RESOURCE_GROUP="your-resource-group"
FUNCTION_APP_NAME="your-function-app-name"

# Create a deployment package
echo "Creating deployment package..."
cd azure-function

# Clean up any existing files
rm -rf .python_packages
rm -f ../function-app.zip

# Create directory for packages
mkdir -p .python_packages/lib/site-packages

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install openai==1.12.0 --target=".python_packages/lib/site-packages"
pip install azure-functions==1.17.0 --target=".python_packages/lib/site-packages"
pip install requests==2.31.0 --target=".python_packages/lib/site-packages"
pip install -r requirements.txt --target=".python_packages/lib/site-packages"

# Create the deployment zip
echo "Creating zip file..."
zip -r ../function-app.zip . -x "*.git*" "*.venv*" "__pycache__/*"

# Go back to root directory
cd ..

# Deploy to Azure
echo "Deploying to Azure Function App: $FUNCTION_APP_NAME"
az functionapp deployment source config-zip \
  --resource-group "$RESOURCE_GROUP" \
  --name "$FUNCTION_APP_NAME" \
  --src "./function-app.zip"

echo "Deployment complete!"