# Manual Troubleshooting for Azure Functions OpenAI Dependency Issue

You're encountering a dependency issue with Azure Functions not being able to find the `openai` module. Here are some manual troubleshooting steps:

## Method 1: Deploy with Pre-installed Dependencies

1. Edit the `deploy_function_app.sh` script in this repo:
   - Update the `RESOURCE_GROUP` and `FUNCTION_APP_NAME` values
   - Run the script:
     ```bash
     ./deploy_function_app.sh
     ```

This script:
- Creates a `.python_packages` directory
- Installs dependencies to the correct location
- Creates a zip package
- Deploys directly to Azure

## Method 2: Use a Python Extension Bundle

1. Add a `extensions.csproj` file to your function app:
   ```xml
   <Project Sdk="Microsoft.NET.Sdk">
     <PropertyGroup>
       <TargetFramework>netcoreapp3.1</TargetFramework>
       <AzureFunctionsVersion>v3</AzureFunctionsVersion>
     </PropertyGroup>
     <ItemGroup>
       <PackageReference Include="Microsoft.Azure.WebJobs.Extensions.Http" Version="3.0.2" />
       <PackageReference Include="Microsoft.NET.Sdk.Functions" Version="3.0.13" />
     </ItemGroup>
   </Project>
   ```

2. Set up extension bundles in your host.json:
   ```json
   {
     "version": "2.0",
     "extensionBundle": {
       "id": "Microsoft.Azure.Functions.ExtensionBundle",
       "version": "[2.*, 3.0.0)"
     }
   }
   ```

## Method 3: Direct Package Installation in Azure

After deployment, you can SSH into your Azure Function App and install packages directly:

1. Enable SSH for your Function App in the Azure Portal
2. Connect via SSH and run:
   ```bash
   cd /home/site/wwwroot
   pip install openai --target=.python_packages/lib/site-packages
   ```

## Method 4: Use a Custom Docker Image

If the above methods don't work, consider moving to a custom Docker image that has all dependencies pre-installed.

## Additional Troubleshooting

- Check the `system_check` function we've added to log detailed information about the Python environment
- Review Azure Function logs for specific import errors
- Verify Python version compatibility (your Azure Function is running Python 3.12)