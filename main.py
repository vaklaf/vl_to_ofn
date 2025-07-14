from pathlib import Path

from assembly_line_reader import run_assebmly_line_reader
from validator import validate_glossaries
from dotenv import load_dotenv
from utilities import create_folder, clear_folder
import os

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
            
def main():
    """ Main entry point for the script."""
    
    settings = prepare_environment()
    print("Starting the assembly line reader...")
    run_assebmly_line_reader(sparql_endpoint=settings["sparql_endpoint"],
                             output_dir=settings["output_dir"],
                             glossaries_file=settings["glossaries_file"],)
    print("Assembly line reading completed.")
    print("Validating glossaries...")
    # Validate glossaries after reading data
    validate_glossaries(glossaries_file=settings["glossaries_file"],
                        report_file=settings["validation_report_file"],
                        output_dir=settings["output_dir"])
    print("Glossaries validation completed.")
    print("All processes completed successfully.")
    
if __name__ == "__main__":
    main()