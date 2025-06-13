from assembly_line_reader import run_assebmly_line_reader
from validator import validate_glossaries

def main():
    """ Main entry point for the script."""
    
    run_assebmly_line_reader()
    validate_glossaries()
    
if __name__ == "__main__":
    main()