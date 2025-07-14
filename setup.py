import os

from pathlib import Path

from dotenv import load_dotenv

from utilities import create_folder, clear_folder

# Load environment variables from .env file
load_dotenv()

def prepare_environment():
    """Prepare the environment by loading necessary configurations."""
    
    # Load environment variables
    sparql_endpoint = os.getenv("SPARQL_ENDPOINT")
    output_dir = os.getenv("OUTPUT_DIR")
    doc_dir = os.getenv("DOC_DIR")
    glossaries_file = os.getenv("GLOSSARIES_FILE")
    validation_report_file = os.getenv("VALIDATION_REPORT_FILE")
    
    if not sparql_endpoint or not output_dir or not doc_dir:
        raise ValueError("Environment variables SPARQL_ENDPOINT, OUTPUT_DIR, and DOC_DIR must be set.")
    
    print(f"SPARQL Endpoint: {sparql_endpoint}")
    print(f"Output Directory: {output_dir}")
    print(f"Documentation Directory: {doc_dir}")
    print(f"Glossaries File: {glossaries_file}")
    print(f"Validation Report File: {validation_report_file}")
    
    # Ensure output and documentation directories exist
    create_folder(output_dir)
    create_folder(doc_dir)
    print("Environment prepared successfully.")
    
    # Clean up old output files
    clear_folder(Path(output_dir))
    clear_folder(Path(doc_dir))

    print("Old output files cleared.") 
    
        
    return {
        "sparql_endpoint": sparql_endpoint,
        "output_dir": output_dir,
        "doc_dir": doc_dir,
        "glossaries_file": glossaries_file,
        "validation_report_file": validation_report_file
    }