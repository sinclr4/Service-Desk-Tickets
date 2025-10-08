import os
from openai import AzureOpenAI
import json

# This tests the OpenAI v1+ API with Azure OpenAI
# Make sure you have environment variables set
try:
    # Setup client using the AzureOpenAI class
    client = AzureOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        api_version=os.environ.get("OPENAI_API_VERSION", "2023-05-15"),
        azure_endpoint=os.environ.get("OPENAI_ENDPOINT")
    )
    
    # Print SDK version
    import openai
    print(f"OpenAI SDK version: {openai.__version__}")
    
    # Test a simple completion
    deployment_id = os.environ.get("OPENAI_MODEL", "gpt-4o")
    response = client.chat.completions.create(
        model=deployment_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ],
        temperature=0.3,
        max_tokens=500,
    )
    
    # Print the response
    print("\nResponse:")
    print(json.dumps(response.model_dump(), indent=2))
    
    # Access the message content properly for v1+ SDK
    content = response.choices[0].message.content.strip()
    print(f"\nMessage content: {content}")

except Exception as e:
    print(f"Error: {str(e)}")