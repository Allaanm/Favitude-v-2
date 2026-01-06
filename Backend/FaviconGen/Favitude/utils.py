import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
from django.http import FileResponse

import os
import platform

def get_font_path(font_name):
    """
    Attempts to find the font file path based on the OS.
    """
    system = platform.system()
    
    # Common font filenames mapping
    font_map = {
        'Roboto': ['Roboto-Regular.ttf', 'arial.ttf'], # Roboto might not be installed
        'Arial': ['arial.ttf', 'Arial.ttf'],
        'Verdana': ['verdana.ttf', 'Verdana.ttf'],
        'Times New Roman': ['times.ttf', 'Times.ttf'],
        'Helvetica': ['Helvetica.ttf', 'arial.ttf', 'Arial.ttf'], # Fallback to Arial on Windows
        'Calibri': ['calibri.ttf', 'Calibri.ttf'],
        'Garamond': ['gara.ttf', 'Garamond.ttf'],
        'Futura': ['Futura.ttf', 'arial.ttf'],
        'Franklin Gothic': ['framd.ttf', 'Franklin Gothic.ttf'],
        'Rockwell': ['rock.ttf', 'Rockwell.ttf'],
    }
    
    potential_filenames = font_map.get(font_name, [f'{font_name}.ttf'])
    
    # Windows Font Directory
    if system == 'Windows':
        font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
        for filename in potential_filenames:
            path = os.path.join(font_dir, filename)
            if os.path.exists(path):
                return path
            # Try capitalizing if not found (sometimes filesystem is picky or map is wrong)
            path_cap = os.path.join(font_dir, filename.capitalize())
            if os.path.exists(path_cap):
                return path_cap
                
    # macOS / Linux could be added here, but user is on Windows.
    # We can perform a robust fallback if needed later.
    
    return None

def generate_favicon_from_image(image_file):
    """
    Generates favicons from an uploaded image file.
    Returns a ZIP file containing .ico and .png formats in standard sizes.
    """
    img = Image.open(image_file)
    sizes = [(16, 16), (32, 32), (96, 96), (256, 256)]
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # ICO file (contains multiple sizes)
        ico_buffer = io.BytesIO()
        # Ensure image is compatible mode
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        img.save(ico_buffer, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        zip_file.writestr('favicon.ico', ico_buffer.getvalue())
        
        # PNGs
        for size in sizes:
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            img_buffer = io.BytesIO()
            resized_img.save(img_buffer, format='PNG')
            zip_file.writestr(f'favicon-{size[0]}x{size[1]}.png', img_buffer.getvalue())
            
    zip_buffer.seek(0)
    return zip_buffer

def generate_favicon_from_text(text, font_size, bg_shape, font_color, bg_color, font_type='Roboto'):
    """
    Generates favicons from text input.
    """
    size = (512, 512) # High resolution base
    img = Image.new('RGBA', size, (0, 0, 0, 0)) # Transparent background initially
    draw = ImageDraw.Draw(img)
    
    # Draw Background
    if bg_shape == 'square':
        draw.rectangle([(0,0), size], fill=bg_color)
    elif bg_shape == 'rounded_square':
        # Draw rounded rectangle (requires corners)
        # Using a simple approximation or standard rounded_rectangle if available in this pillow version
        # Radius ~ 20% of size is standard for icons
        r = 100 
        draw.rounded_rectangle([(0,0), size], radius=r, fill=bg_color)
    elif bg_shape == 'circle':
        draw.ellipse([(0,0), size], fill=bg_color)
    elif bg_shape == 'triangular':
        # Triangle pointing up
        draw.polygon([(256, 0), (0, 512), (512, 512)], fill=bg_color)
    else:
        # Default to square if unknown
        draw.rectangle([(0,0), size], fill=bg_color)
        
    # Determine Font
    font_path = get_font_path(font_type)
    
    # Auto-fit logic if font_size is not provided or 0
    target_size_px = 300 # Default fallback
    
    if font_size and int(font_size) > 0:
        # Manual size - scale it up because user input 100 usually means "big", but on 512 canvas it's different.
        # We'll treat user input roughly as percentage of canvas if > 10, or pt size.
        # Let's align with previous logic: * 10 was a bit aggressive if they type 200.
        # If they type "50", 50*10 = 500 (full height).
        target_size_px = int(font_size)
    
    # If using 'None' (default), we try to find the max size that fits.
    # However, to do that efficiently we need a Font object.
    
    final_font = None
    
    # Load initial font to test or use
    try:
        if font_path:
            # If auto-sizing, start big and shrink, or binary search. 
            # Simple approach: Start at 400 and shrink until it fits box (e.g. 400x400 safe area)
             
            if not font_size or int(font_size) <= 0:
                # AUTO SIZE
                test_size = 400
                while test_size > 10:
                    f = ImageFont.truetype(font_path, test_size)
                    # Get bbox
                    left, top, right, bottom = draw.textbbox((0, 0), text, font=f)
                    w = right - left
                    h = bottom - top
                    if w < 450 and h < 450: # Leave some padding
                        final_font = f
                        break
                    test_size -= 20
            else:
                final_font = ImageFont.truetype(font_path, target_size_px)
        else:
             final_font = ImageFont.load_default()
             # Default font is fixed size, can't scale easily without hacks.
             
    except Exception:
        final_font = ImageFont.load_default()
    
    if final_font is None:
         # Fallback if auto-sizing loop failed to set it (unlikely)
         final_font = ImageFont.load_default()

    # Draw Text Centered
    # anchor='mm' aligns the text's middle-center to the given xy coordinates
    # This is much more accurate than manual calculation
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Adjust for visual center if triangle
    if bg_shape == 'triangular':
        center_y = int(size[1] * 0.65) # Move text down a bit for triangle

    draw.text((center_x, center_y), text, fill=font_color, font=final_font, anchor='mm')
    
    # Process like image
    sizes = [(16, 16), (32, 32), (96, 96), (256, 256)]
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
         # ICO
        ico_buffer = io.BytesIO()
        img.save(ico_buffer, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        zip_file.writestr('favicon.ico', ico_buffer.getvalue())

        for s in sizes:
            resized = img.resize(s, Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            resized.save(buf, format='PNG')
            zip_file.writestr(f'favicon-{s[0]}x{s[1]}.png', buf.getvalue())
            
    zip_buffer.seek(0)
    return zip_buffer
