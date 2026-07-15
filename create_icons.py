#!/usr/bin/env python3
"""
Simple icon generator for PWA using PIL (Pillow)
Creates basic icons with the app logo/text for different sizes
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Create a simple icon with the app logo"""
    # Create a new image with green background
    img = Image.new('RGB', (size, size), color='#198754')
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default
    try:
        # Try different font paths for different systems
        font_paths = [
            '/System/Library/Fonts/Arial.ttf',  # macOS
            'C:/Windows/Fonts/arial.ttf',       # Windows
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        ]
        
        font_size = max(size // 8, 12)
        font = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        
        if font is None:
            font = ImageFont.load_default()
            
    except Exception:
        font = ImageFont.load_default()
    
    # Draw recycling symbol or E-W text
    if size >= 72:
        # Draw a simple recycling symbol using text
        text = "♻"
        if size >= 144:
            try:
                font = ImageFont.truetype(font_paths[1] if os.path.exists(font_paths[1]) else font_paths[0], size // 3)
            except:
                pass
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font)
        
        # Add "E-W" text below if there's space
        if size >= 144:
            small_font_size = max(size // 12, 10)
            try:
                small_font = ImageFont.truetype(font_paths[1] if os.path.exists(font_paths[1]) else font_paths[0], small_font_size)
            except:
                small_font = font
            
            small_text = "E-W"
            bbox = draw.textbbox((0, 0), small_text, font=small_font)
            small_text_width = bbox[2] - bbox[0]
            
            small_x = (size - small_text_width) // 2
            small_y = y + text_height + 10
            
            if small_y + small_font_size < size:
                draw.text((small_x, small_y), small_text, fill='white', font=small_font)
    else:
        # For small icons, just draw a simple circle
        margin = size // 6
        draw.ellipse([margin, margin, size - margin, size - margin], fill='white')
    
    # Save the image
    img.save(output_path, 'PNG')
    print(f"Created icon: {output_path} ({size}x{size})")

def main():
    """Generate all required PWA icons"""
    icon_sizes = [16, 32, 72, 96, 128, 144, 152, 192, 384, 512]
    icons_dir = 'frontend/static/icons'
    
    # Create icons directory if it doesn't exist
    os.makedirs(icons_dir, exist_ok=True)
    
    # Generate icons for each size
    for size in icon_sizes:
        output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        create_icon(size, output_path)
    
    print(f"\nGenerated {len(icon_sizes)} PWA icons in {icons_dir}/")
    print("Icons are ready for use in the PWA manifest!")

if __name__ == '__main__':
    main()
