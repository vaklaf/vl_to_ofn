from pathlib import Path
from uuid import uuid4

def generate_target_filename(output_dir, extension="json-ld")->Path:
    """Create a target filename with the given base name and extension."""
    name = str(uuid4())   
    print(f"Generating target filename: {name}.{extension} in {output_dir}")
    # Ensure the output directory ends with a slash
    if not output_dir.endswith('/'):
        output_dir += '/'
        
    return Path(str(output_dir[:-1])) /  f"{name}.{extension}"
        
def create_folder(folder:str)->Path:
    # Create the output directory if it doesn't exist
    output_dir = Path.cwd() / folder
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def clear_folder(folder: Path):
    """Clear the output folder by removing all files in it."""
    for file in folder.glob("*"):
        if file.is_file():
            file.unlink()
    print(f"Output folder {folder} cleared.")
        
    