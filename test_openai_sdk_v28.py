import os
import openai
import json

# This tests the OpenAI v0.28.1 API with Azure OpenAI
# Make sure you have environment variables set
try:
    # Setup client using the global API settings approach
    openai.api_type = "azure"
    openai.api_key = os.environ.get("OPENAI_API_KEY") 
    openai.api_version = os.environ.get("OPENAI_API_VERSION", "2023-05-15")
    openai.api_base = os.environ.get("OPENAI_ENDPOINT")
    
    # Print SDK version
    print(f"OpenAI SDK version: {openai.__version__}")
    
    # Test a simple completion
    deployment_id = os.environ.get("OPENAI_MODEL", "gpt-4o")
    response = openai.ChatCompletion.create(
        engine=deployment_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ],
        temperature=0.3,
        max_tokens=500,
    )
    
    # Print the response
    print("\nResponse:")
    print(json.dumps(response, indent=2, default=str))
    
    # Access the message content properly for v0.28.1
    content = response.choices[0].message['content'].strip()
    print(f"\nMessage content: {content}")

except Exception as e:
    print(f"Error: {str(e)}")