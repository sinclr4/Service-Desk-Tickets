import azure.functions as func
import logging
import csv
import os
import io
import tempfile
import json
import time
from openai import AzureOpenAI

app = func.FunctionApp()

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

def classify_ticket(description, openai_client):
    """Classify a ticket using Azure OpenAI"""
    prompt = f"""
Classify the following service desk ticket into one of these categories:
{', '.join(CATEGORIES)}

Ticket Description:
{description}

Category:
"""
    try:
        response = openai_client.chat.completions.create(
            model=os.environ["OPENAI_MODEL"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        logging.error(f"Error classifying ticket: {str(e)}")
        return "Classification Error"

@app.route(route="classify_tickets", auth_level=func.AuthLevel.FUNCTION)
def classify_tickets(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processing a request.')
    
    try:
        # Get the request body
        req_body = req.get_body()
        
        # Check if there's a file in the request
        if not req_body:
            return func.HttpResponse(
                "Please pass a CSV file in the request body",
                status_code=400
            )
        
        # Create Azure OpenAI client
        client = AzureOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            api_version=os.environ["OPENAI_API_VERSION"],
            azure_endpoint=os.environ["OPENAI_ENDPOINT"],
            timeout=30.0
        )
        
        # Process the CSV file
        input_stream = io.StringIO(req_body.decode('utf-8'))
        output_stream = io.StringIO()
        
        reader = csv.DictReader(input_stream)
        
        # Check for Description column
        if 'Description' not in reader.fieldnames:
            return func.HttpResponse(
                "CSV must contain a 'Description' column",
                status_code=400
            )
            
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
                category = classify_ticket(description, client)
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

@app.route(route="classify_single", auth_level=func.AuthLevel.FUNCTION)
def classify_single(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processing a single ticket classification request.')
    
    try:
        # Get the request body
        req_body = req.get_json()
        
        if not req_body or 'description' not in req_body:
            return func.HttpResponse(
                "Please pass a description in the request body",
                status_code=400
            )
        
        # Create Azure OpenAI client
        client = AzureOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            api_version=os.environ["OPENAI_API_VERSION"],
            azure_endpoint=os.environ["OPENAI_ENDPOINT"],
            timeout=30.0
        )
        
        description = req_body['description']
        category = classify_ticket(description, client)
        
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