from pathlib import Path
from uuid import uuid4

def create_target_filename(output_dir, extension="jsonld")->Path:
    """Create a target filename with the given base name and extension."""
    name = str(uuid4())   
    return output_dir /  f"{name}.{extension}"
        
def create_output_folder()->Path:
    # Create the output directory if it doesn't exist
    output_dir = Path.cwd() / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def clear_output_folder(output_dir: Path):
    """Clear the output folder by removing all files in it."""
    for file in output_dir.glob("*"):
        if file.is_file():
            file.unlink()
    print(f"Output folder {output_dir} cleared.")
        
    