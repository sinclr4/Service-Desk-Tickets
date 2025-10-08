import logging
import azure.functions as func
import json
import os
import sys

# Add the site-packages to the path if needed
site_packages_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  '.python_packages', 'lib', 'site-packages')
if os.path.exists(site_packages_path) and site_packages_path not in sys.path:
    sys.path.append(site_packages_path)

try:
    from openai import AzureOpenAI
except ImportError:
    logging.error("Failed to import OpenAI. Path: %s", sys.path)
    raise

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for single classification.')

    # Define categories
    CATEGORIES = [
        "NHSUK Spam/Marketing",
        "NHSUK Profiles",
        "NHSuk Unsupported Service",
        "NHSUK Content Management Service",
        "NHSUK Data Services - Directories",
        "NHSUK Ratings & Reviews",
        "NHSuk Generic Service",
        "NHSUK Data Services - GDoS",
        "NHSUK Personal Medical Query",
        "NHSUK Find A Service",
        "NHSUK Syndication",
        "NHSUK Health Assessment Tools",
        "NHSUK Internal Tech Request",
        "NHSUK Find Your NHS Number",
        "Z_Retired P0 & P5 Web Service",
        "NBS Q-Flow Acct Mgmt",
        "NSD Unsupported Service",
        "NBS Patient Journey",
        "NHSUK Give Us Feedback Form",
        "NHSUK Campaigns",
        "Patient Facing",
        "Profile manager (GP Reg)",
        "NHS App National Services",
        "GeneralPracticeAnnualSelfDeclaration-eDec",
        "NHSUK Authenticated Website",
        "Post event message to GP",
        "CSF – Junk NSD"
    ]

    try:
        # Get the request body
        req_body = req.get_json()
        
        if not req_body or 'description' not in req_body:
            return func.HttpResponse(
                "Please pass a description in the request body",
                status_code=400
            )
        
        # Log environment variables for debugging (hiding API key)
        logging.info(f"API Version: {os.environ.get('OPENAI_API_VERSION')}")
        logging.info(f"Endpoint: {os.environ.get('OPENAI_ENDPOINT')}")
        logging.info(f"Model: {os.environ.get('OPENAI_MODEL')}")
        
        # Check for any proxy environment variables
        proxy_vars = [var for var in os.environ if 'proxy' in var.lower()]
        if proxy_vars:
            logging.info(f"Found proxy environment variables: {', '.join(proxy_vars)}")
        
        # Disable proxies by setting environment variables
        os.environ['no_proxy'] = '*'
        
        # Log httpx version if available
        try:
            import httpx
            logging.info(f"httpx version: {httpx.__version__}")
        except ImportError:
            logging.info("httpx not directly importable")
        
        # Create Azure OpenAI client using the new SDK
        # Using the default HTTP client now that we've pinned httpx to a compatible version
        client = AzureOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            api_version=os.environ["OPENAI_API_VERSION"],
            azure_endpoint=os.environ["OPENAI_ENDPOINT"]
        )
        
        description = req_body['description']
        
        # Classify the ticket
        prompt = f"""
Classify the following service desk ticket into one of these categories:
{', '.join(CATEGORIES)}

Ticket Description:
{description}

Category:
"""
        try:
            deployment_id = os.environ.get("OPENAI_MODEL", "gpt-4o")
            response = client.chat.completions.create(
                model=deployment_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0
            )
            category = response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error classifying ticket: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            # Log additional details if it's a proxies error
            if "proxies" in str(e).lower():
                logging.error("This appears to be a proxies-related error. Make sure no proxy settings are conflicting.")
            category = "Classification Error"
        
        # Return the category
        return func.HttpResponse(
            json.dumps({"category": category}),
            mimetype="application/json",
            status_code=200
        )
            
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            f"Error processing request: {str(e)}",
            status_code=500
        )