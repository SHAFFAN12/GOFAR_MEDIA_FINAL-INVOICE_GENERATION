from pathlib import Path
import sys

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