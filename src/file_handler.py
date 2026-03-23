import uuid
import base64
from pathlib import Path

IMAGES_DIR = Path(__file__).parent.parent / "images"


def generate_unique_filename(original_name):
    ext = original_name.lower().split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    return unique_name


def save_file(file_data, filename):
    IMAGES_DIR.mkdir(exist_ok=True)
    unique_name = generate_unique_filename(filename)
    filepath = IMAGES_DIR / unique_name

    with open(filepath, "wb") as f:
        f.write(file_data)

    return unique_name


def delete_file(filename):
    filepath = IMAGES_DIR / filename
    if filepath.exists():
        filepath.unlink()
        return True
    return False


def list_images_with_preview():
    files = []
    for file_path in IMAGES_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif"]:
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            files.append({
                "name": file_path.name,
                "preview": f"data:image/{file_path.suffix[1:]};base64,{encoded}"
            })
    return files
