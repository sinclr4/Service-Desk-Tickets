import logging
import azure.functions as func
import io
import json
import csv
import time
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

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

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
        # Get the CSV file content
        csv_content = req.get_body().decode('utf-8')
        
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
        
        # Create Azure OpenAI client using the new SDK
        api_key = os.environ["OPENAI_API_KEY"]
        api_version = os.environ["OPENAI_API_VERSION"]
        azure_endpoint = os.environ["OPENAI_ENDPOINT"]
        
        # Initialize client with default_headers to avoid proxies issue
        # Removing the custom HTTP client since it's causing issues
        try:
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                default_headers={"Accept": "application/json"}
            )
            # Test the client with a simple API call
            logging.info("Testing OpenAI client initialization...")
        except Exception as e:
            logging.error(f"Error initializing OpenAI client: {str(e)}")
            raise
        
        # Process the CSV
        input_stream = io.StringIO(csv_content)
        output_stream = io.StringIO()
        
        reader = csv.DictReader(input_stream)
        fieldnames = reader.fieldnames + ['Category']
        writer = csv.DictWriter(output_stream, fieldnames=fieldnames)
        writer.writeheader()
        
        # Get optional limit parameter
        limit = req.params.get('limit')
        limit = int(limit) if limit else None
        
        count = 0
        for row in reader:
            # Check if we've reached the limit
            if limit and count >= limit:
                break
                
            description = row.get('Description', '')
            if description:
                # Classify the ticket
                system_message = "You are a helpful assistant that classifies service desk tickets into predefined categories."
                ticket_prompt = f"""
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
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": ticket_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=500,
                    )
                    category = response.choices[0].message.content.strip()
                except Exception as e:
                    logging.error(f"Error classifying ticket: {str(e)}")
                    logging.error(f"Error type: {type(e).__name__}")
                    # Log additional details if it's a proxies error
                    if "proxies" in str(e).lower():
                        logging.error("This appears to be a proxies-related error. Make sure no proxy settings are conflicting.")
                    category = "Classification Error"
                
                # Add a small delay to avoid rate limits
                time.sleep(0.5)
            else:
                category = "No Description"
                
            row['Category'] = category
            writer.writerow(row)
            count += 1
            
        # Return the processed CSV
        return func.HttpResponse(
            output_stream.getvalue(),
            mimetype="text/csv",
            status_code=200
        )
            
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            f"Error processing request: {str(e)}",
            status_code=500
        )