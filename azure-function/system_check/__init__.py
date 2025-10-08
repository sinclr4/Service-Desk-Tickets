import logging
import azure.functions as func
import os
import sys
import json

# Log system path info
def log_sys_info():
    logging.info("Python version: %s", sys.version)
    logging.info("Python path: %s", sys.path)
    logging.info("Current directory: %s", os.getcwd())
    logging.info("Directory contents: %s", os.listdir('.'))
    
    # Check for .python_packages
    packages_dir = os.path.join(os.getcwd(), '.python_packages')
    if os.path.exists(packages_dir):
        logging.info(".python_packages exists: %s", os.listdir(packages_dir))
        site_packages = os.path.join(packages_dir, 'lib', 'site-packages')
        if os.path.exists(site_packages):
            logging.info("site-packages exists: %s", os.listdir(site_packages))
    else:
        logging.info(".python_packages does not exist")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    log_sys_info()

    # Try importing different modules to debug
    modules_to_try = [
        'azure.functions', 
        'openai', 
        'httpx',
        'requests', 
        'json', 
        'os',
        'sys'
    ]
    
    results = {}
    for module_name in modules_to_try:
        try:
            module = __import__(module_name)
            if module_name == 'openai':
                results[module_name] = f"Success - Version {module.__version__}"
            else:
                results[module_name] = "Success"
        except ImportError as e:
            results[module_name] = f"Failed: {str(e)}"
        except AttributeError as e:
            results[module_name] = f"Success (no __version__)"

    # Test httpx Client with proxies parameter
    httpx_proxies_test = "Not tested"
    try:
        import httpx
        try:
            # Try to create a client with proxies parameter
            client = httpx.Client(proxies=None)
            httpx_proxies_test = "Supports proxies=None"
        except TypeError as e:
            httpx_proxies_test = f"Error: {str(e)}"
    except ImportError:
        httpx_proxies_test = "httpx not available"
    
    response_body = {
        "status": "System Check",
        "python_version": sys.version,
        "module_checks": results,
        "httpx_proxies_test": httpx_proxies_test
    }
    
    import json
    return func.HttpResponse(
        json.dumps(response_body),
        mimetype="application/json",
        status_code=200
    )