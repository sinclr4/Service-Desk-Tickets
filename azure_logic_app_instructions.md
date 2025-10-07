# Using the Ticket Classification Azure Function with Logic App

## Azure Function Setup

1. **Create a new Azure Function app** in Azure Portal
   - Create a new Function App resource
   - Runtime stack: Python
   - Version: Python 3.10+

2. **Deploy the Function Code**
   - Upload the code from the `azure-function` folder
   - Add application settings (in Configuration):
     - OPENAI_API_KEY: Your Azure OpenAI API key
     - OPENAI_API_VERSION: 2025-01-01-preview
     - OPENAI_ENDPOINT: `https://nhsuk-ai-ap-uks.openai.azure.com/`
     - OPENAI_MODEL: gpt-4o

3. **Test the Function**
   - Test both HTTP endpoints:
     - `/api/classify_tickets` - Takes a CSV file and returns categorized CSV
     - `/api/classify_single` - Takes a JSON with a description and returns a category

## Logic App Setup (For Batch Processing)

1. **Create a new Logic App** in Azure Portal

2. **Design the Logic App workflow**:

```yaml
Trigger: When a file is added to a location (OneDrive, SharePoint, etc.)
↓
Get file content (using the connector for your storage)
↓
HTTP action:
  - Method: POST
  - URI: https://your-function-app.azurewebsites.net/api/classify_tickets?code=YOUR_FUNCTION_KEY
  - Body: Content of the CSV file
  - Headers: Content-Type: text/csv
↓
Create file (Save the processed CSV to your storage)
```

3. **Save and test** the Logic App workflow

## Logic App Setup (For Individual Ticket Processing)

1. **Create a new Logic App** in Azure Portal

2. **Design the Logic App workflow**:

```yaml
Trigger: When a new item is created (SharePoint list, Dataverse, etc.)
↓
HTTP action:
  - Method: POST
  - URI: https://your-function-app.azurewebsites.net/api/classify_single?code=YOUR_FUNCTION_KEY
  - Body: {"description": "@{triggerBody()?['Description']}"}
  - Headers: Content-Type: application/json
↓
Update item (Update the original item with the category)
```

3. **Save and test** the Logic App workflow