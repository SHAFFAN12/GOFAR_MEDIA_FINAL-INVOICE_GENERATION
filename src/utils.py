from pathlib import Path
import sys


def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        # Not in a PyInstaller bundle, so the base path is the project root
        base_path = Path(__file__).parent.parent

    return str(base_path / relative_path)


def get_scale(img, page_rect):
    img_w, img_h = img.size
    scale_x = page_rect.width / img_w
    scale_y = page_rect.height / img_h
    return scale_x, scale_y

def get_output_dir() -> Path:
    """Gets the directory for generated documents."""
    if hasattr(sys, '_MEIPASS'):
        # For bundled app, create docs folder next to the executable
        output_dir = Path(sys.executable).parent / "generated_docs"
    else:
        # For development, create it at the project root
        output_dir = Path(__file__).parent.parent / "generated_docs"
    
    output_dir.mkdir(exist_ok=True)
    return output_dir

from PIL import Image

def convert_png_to_ico(png_path: str, ico_path: str):
    """Converts a PNG image to an ICO file with multiple sizes."""
    try:
        img = Image.open(png_path)
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        print(f"Successfully converted {png_path} to {ico_path}")
        return True
    except Exception as e:
        print(f"Error converting PNG to ICO: {e}")
        return False
