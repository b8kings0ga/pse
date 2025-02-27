"""
Creates an icon for the application.
This is a utility script that generates a simple icon file for the application.
"""
import os
import sys
import platform
import subprocess
import tempfile
from PIL import Image, ImageDraw

def create_app_icon():
    """Create a simple icon for the application in various formats"""
    
    # Create icon directory if it doesn't exist
    icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
    os.makedirs(icon_dir, exist_ok=True)
    
    # Create a 256x256 image with a transparent background
    icon = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw a rounded rectangle as background
    draw.rounded_rectangle(
        [(20, 20), (236, 236)],
        fill=(52, 152, 219),  # Blue
        outline=(41, 128, 185),
        width=4,
        radius=30
    )
    
    # Draw slide icon
    draw.rectangle(
        [(70, 70), (186, 140)],
        fill=(255, 255, 255),
        outline=(41, 128, 185),
        width=2
    )
    
    # Draw camera/video icon
    draw.ellipse(
        [(98, 158), (158, 218)],
        fill=(231, 76, 60),  # Red
        outline=(192, 57, 43),
        width=2
    )
    
    # Draw a simple lens symbol
    draw.ellipse(
        [(114, 174), (142, 202)],
        fill=(231, 76, 60),
        outline=(255, 255, 255),
        width=2
    )
    
    # Save as PNG for development and other formats as needed
    png_path = os.path.join(icon_dir, 'app_icon.png')
    ico_path = os.path.join(icon_dir, 'app_icon.ico')
    icns_path = os.path.join(icon_dir, 'app_icon.icns')
    
    # Save the PNG version
    icon.save(png_path, 'PNG')
    print(f"Icon saved as PNG: {png_path}")
    
    # Create different formats based on platform
    current_platform = platform.system()
    
    # For Windows: Create ICO file
    if current_platform == "Windows" or "win" in sys.platform:
        # Create multiple sizes for ICO
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []
        
        for size in icon_sizes:
            resized_icon = icon.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized_icon)
        
        # Save as ICO with multiple sizes
        icons[0].save(
            ico_path,
            format='ICO',
            sizes=[(i.width, i.height) for i in icons],
            append_images=icons[1:]
        )
        print(f"Icon saved as ICO: {ico_path}")
    
    # For macOS: Create ICNS file
    if current_platform == "Darwin" or "darwin" in sys.platform:
        try:
            # Method 1: Using iconutil if available
            create_macos_icon_using_iconutil(icon, icon_dir, icns_path)
        except Exception as e:
            print(f"Error creating ICNS using iconutil: {e}")
            try:
                # Method 2: Direct creation with Pillow if supported
                create_macos_icon_using_pillow(icon, icns_path)
            except Exception as e:
                print(f"Error creating ICNS using Pillow: {e}")
                # Fallback to PNG
                print("Using PNG icon as fallback")
                return png_path
    
    # Return the appropriate icon path based on platform
    if current_platform == "Darwin":
        return icns_path if os.path.exists(icns_path) else png_path
    elif current_platform == "Windows":
        return ico_path
    else:
        return png_path

def create_macos_icon_using_iconutil(icon, icon_dir, icns_path):
    """Create macOS ICNS icon using iconutil command-line tool"""
    # Create temporary iconset directory
    iconset_dir = os.path.join(icon_dir, 'app.iconset')
    os.makedirs(iconset_dir, exist_ok=True)
    
    # Required sizes for macOS icons
    icon_sizes = {
        16: 'icon_16x16.png',
        32: 'icon_16x16@2x.png',  # 32x32
        32: 'icon_32x32.png',
        64: 'icon_32x32@2x.png',  # 64x64
        128: 'icon_128x128.png',
        256: 'icon_128x128@2x.png',  # 256x256
        256: 'icon_256x256.png',
        512: 'icon_256x256@2x.png',  # 512x512
        512: 'icon_512x512.png',
        1024: 'icon_512x512@2x.png',  # 1024x1024
    }
    
    # Create each required size and save to iconset
    for size, filename in icon_sizes.items():
        resized_icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        resized_icon.save(os.path.join(iconset_dir, filename), 'PNG')
    
    # Convert iconset to icns using iconutil
    subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', icns_path], check=True)
    print(f"Icon saved as ICNS: {icns_path}")
    
    # Clean up the iconset directory
    for file in os.listdir(iconset_dir):
        os.remove(os.path.join(iconset_dir, file))
    os.rmdir(iconset_dir)

def create_macos_icon_using_pillow(icon, icns_path):
    """Create macOS ICNS icon directly using Pillow if supported"""
    # This method may not work with all versions of Pillow
    # but we'll include it as an alternative
    icon.save(icns_path, format='ICNS')
    print(f"Icon saved as ICNS using Pillow: {icns_path}")

if __name__ == '__main__':
    create_app_icon()
