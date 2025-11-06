#!/usr/bin/env python3
"""
Visual test to verify bitmap icon rendering.
Creates PNG images of each icon for visual verification.
"""

from PIL import Image
from icon_bitmaps import ICON_MAP

def render_bitmap_to_image(bitmap_data, width=32, height=32, scale=4):
    """
    Render a bitmap to a PIL Image for visualization.
    
    Args:
        bitmap_data: bytearray of bitmap data
        width: Bitmap width in pixels
        height: Bitmap height in pixels
        scale: Scale factor for output image
    
    Returns:
        PIL Image
    """
    # Create image (scaled up for visibility)
    img = Image.new('RGB', (width * scale, height * scale), color='white')
    pixels = img.load()
    
    byte_width = (width + 7) // 8
    
    # Render each pixel
    for row in range(height):
        for col in range(width):
            byte_idx = row * byte_width + (col // 8)
            bit_idx = 7 - (col % 8)
            
            if byte_idx < len(bitmap_data):
                pixel_value = (bitmap_data[byte_idx] >> bit_idx) & 1
                
                # Draw scaled pixel
                color = (0, 0, 0) if pixel_value else (255, 255, 255)
                for dy in range(scale):
                    for dx in range(scale):
                        pixels[col * scale + dx, row * scale + dy] = color
    
    return img

def main():
    """Render all icons to PNG files"""
    import os
    
    output_dir = '/tmp/icon_previews'
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 Rendering bitmap icons to PNG files...")
    print(f"Output directory: {output_dir}\n")
    
    for symbol, bitmap in sorted(ICON_MAP.items()):
        # Create safe filename
        safe_name = symbol.replace('/', '_').replace('<', 'lt').replace('>', 'gt')
        safe_name = safe_name.replace('[', 'lb').replace(']', 'rb').replace('^', 'up')
        safe_name = safe_name.replace('*', 'star').replace('=', 'eq').replace('★', 'star')
        safe_name = safe_name.replace('#', 'hash').replace('~', 'tilde').replace('%', 'pct')
        # 'o' is already safe, no replacement needed
        
        filename = f"{output_dir}/icon_{safe_name}.png"
        
        # Render bitmap
        img = render_bitmap_to_image(bitmap, scale=8)
        img.save(filename)
        
        print(f"✅ Rendered '{symbol}' -> {filename}")
    
    print(f"\n✨ Done! All icons rendered to {output_dir}")
    print(f"View them with: ls -lh {output_dir}")

if __name__ == '__main__':
    main()
