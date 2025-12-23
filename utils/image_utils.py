"""
Image utilities for Nano Banana Batch Processor.
Handles image validation, thumbnails, and format conversion.
"""

from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ExifTags
import io


# Supported image formats (lowercase only - we convert to lowercase for comparison)
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif'}


def is_supported_image(path: str) -> bool:
    """Check if a file is a supported image format (case-insensitive)."""
    return Path(path).suffix.lower() in SUPPORTED_FORMATS


def get_supported_extensions() -> str:
    """Get file dialog filter string for supported formats (both cases)."""
    extensions_lower = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_FORMATS))
    extensions_upper = " ".join(f"*{ext.upper()}" for ext in sorted(SUPPORTED_FORMATS))
    return f"Images ({extensions_lower} {extensions_upper})"


def filter_supported_images(paths: List[str]) -> List[str]:
    """Filter a list of paths to only include supported images."""
    return [p for p in paths if is_supported_image(p)]


def apply_exif_orientation(img: Image.Image) -> Image.Image:
    """
    Apply EXIF orientation to an image.
    This corrects the rotation for photos taken in portrait mode.
    
    Args:
        img: PIL Image object
    
    Returns:
        Correctly oriented PIL Image
    """
    try:
        # Get EXIF data
        exif = img._getexif()
        if exif is None:
            return img
        
        # Find orientation tag
        orientation_key = None
        for key, val in ExifTags.TAGS.items():
            if val == 'Orientation':
                orientation_key = key
                break
        
        if orientation_key is None or orientation_key not in exif:
            return img
        
        orientation = exif[orientation_key]
        
        # Apply rotation based on orientation
        if orientation == 2:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 4:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            img = img.rotate(-90, expand=True)
        elif orientation == 7:
            img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            img = img.rotate(90, expand=True)
        
        return img
    except Exception:
        return img


def create_thumbnail(image_path: str, size: Tuple[int, int] = (150, 150)) -> Optional[bytes]:
    """
    Create a thumbnail from an image file.
    
    Args:
        image_path: Path to the image file
        size: Maximum thumbnail size (width, height)
    
    Returns:
        PNG bytes of the thumbnail, or None if failed
    """
    try:
        with Image.open(image_path) as img:
            # Apply EXIF orientation first
            img = apply_exif_orientation(img)
            
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ('RGBA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()
    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {e}")
        return None


def get_image_info(image_path: str) -> Optional[dict]:
    """
    Get information about an image.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Dictionary with image info, or None if failed
    """
    try:
        path = Path(image_path)
        with Image.open(image_path) as img:
            return {
                "filename": path.name,
                "path": str(path),
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": path.stat().st_size,
            }
    except Exception as e:
        print(f"Error getting image info for {image_path}: {e}")
        return None


def validate_image(image_path: str) -> Tuple[bool, str]:
    """
    Validate that a file is a valid, readable image.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(image_path)
    
    if not path.exists():
        return False, "Le fichier n'existe pas"
    
    if not path.is_file():
        return False, "Ce n'est pas un fichier"
    
    if not is_supported_image(image_path):
        return False, f"Format non supporté. Formats acceptés: {', '.join(SUPPORTED_FORMATS)}"
    
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True, ""
    except Exception as e:
        return False, f"Image corrompue ou illisible: {e}"


def generate_output_filename(input_path: str, suffix: str = "_processed") -> str:
    """
    Generate an output filename based on the input path.
    
    Args:
        input_path: Original image path
        suffix: Suffix to add before extension
    
    Returns:
        New filename (just the name, not full path)
    """
    path = Path(input_path)
    return f"{path.stem}{suffix}.png"
