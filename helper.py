from pathlib import Path

def clean_folder(folder_path: Path):
    for item in folder_path.iterdir():
        if item.is_file():
            item.unlink()  # Deletes the file