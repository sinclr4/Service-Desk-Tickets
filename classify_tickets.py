import csv
import configparser
import openai
import time
import os

# Use absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.ini")
CSV_PATH = os.path.join(BASE_DIR, "NHS.UK ServiceNow Cases Q1 2025.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "NHS.UK ServiceNow Cases Q1 2025 - Categorized.csv")
DESCRIPTION_COL = "Description"
CATEGORY_COL = "Category"

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

def load_config(path):
    print(f"Loading configuration from: {path}")
    config = configparser.ConfigParser()
    config.read(path)
    
    if 'azure_openai' not in config:
        raise ValueError(f"azure_openai section not found in config file: {path}")
    
    required_keys = ['endpoint', 'api_key', 'model', 'api_version']
    config_section = config['azure_openai']
    
    for key in required_keys:
        if key not in config_section or not config_section[key]:
            raise ValueError(f"Missing or empty {key} in config file")
    
    # Print config details (careful with API key)
    safe_config = dict(config_section)
    if 'api_key' in safe_config:
        api_key = safe_config['api_key']
        if len(api_key) > 8:
            safe_config['api_key'] = api_key[:4] + '...' + api_key[-4:]
        else:
            safe_config['api_key'] = '********'
    
    print(f"Config loaded: {safe_config}")
    return config_section

def classify_ticket(description, openai_config):
    prompt = f"""
Classify the following service desk ticket into one of these categories:
{', '.join(CATEGORIES)}

Ticket Description:
{description}

Category:
"""
    print(f"Connecting to Azure OpenAI at: {openai_config['endpoint']}")
    print(f"Using model: {openai_config['model']}")
    
    try:
        client = openai.AzureOpenAI(
            api_key=openai_config['api_key'],
            api_version=openai_config['api_version'],
            azure_endpoint=openai_config['endpoint'],
            timeout=30.0  # Add a 30-second timeout
        )
        
        print("Sending request to Azure OpenAI...")
        response = client.chat.completions.create(
            model=openai_config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        print(f"Connection error details: {str(e)}")
        raise

def main():
    try:
        print(f"Starting ticket classification process...")
        print(f"CSV file: {CSV_PATH}")
        print(f"Output file: {OUTPUT_PATH}")
        
        # Check if the CSV file exists
        if not os.path.exists(CSV_PATH):
            print(f"Error: CSV file does not exist at {CSV_PATH}")
            return
            
        openai_config = load_config(CONFIG_PATH)

        with open(CSV_PATH, newline='', encoding='utf-8') as infile, \
             open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            
            # Verify Description column exists
            if DESCRIPTION_COL not in reader.fieldnames:
                print(f"Error: '{DESCRIPTION_COL}' column not found in CSV. Available columns: {reader.fieldnames}")
                return
                
            fieldnames = reader.fieldnames + [CATEGORY_COL]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            count = 0
            for row in reader:
                if count >= 20:
                    break
                    
                print(f"\nProcessing ticket {count + 1}/20...")
                description = row.get(DESCRIPTION_COL, "")
                if description:
                    print(f"Description: {description[:100]}..." if len(description) > 100 else f"Description: {description}")
                    try:
                        category = classify_ticket(description, openai_config)
                        print(f"Classified as: {category}")
                    except Exception as e:
                        print(f"Error classifying ticket: {e}")
                        category = "Error"
                    time.sleep(1)  # avoid rate limits
                else:
                    print("No description found")
                    category = "No Description"
                    
                row[CATEGORY_COL] = category
                writer.writerow(row)
                count += 1
                
        print(f"\nClassification complete. Processed {count} tickets.")
        print(f"Results written to: {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
