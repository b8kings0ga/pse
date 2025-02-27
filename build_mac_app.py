"""
Build script specifically for creating a macOS application bundle.
This script includes optimizations for macOS.
"""
import os
import sys
import subprocess
import shutil
import platform
from app_icon import create_app_icon

def build_mac_app():
    """Build the macOS application bundle"""
    if platform.system() != "Darwin":
        print("This script is intended for macOS only.")
        return False
    
    print("Starting build process for macOS application...")
    
    # Create icon
    print("Creating application icon...")
    icon_path = create_app_icon()
    
    if not icon_path or not os.path.exists(icon_path):
        print("Warning: Could not create icon, proceeding without custom icon")
        icon_path = None
    else:
        print(f"Using icon: {icon_path}")
    
    # Ensure the dist directory is clean
    if os.path.exists('dist'):
        print("Cleaning previous build...")
        shutil.rmtree('dist')
    
    # PyInstaller arguments for macOS
    pyinstaller_args = [
        'pyinstaller',
        '--name=SlideExtractor',
        '--onefile',
        '--windowed',
        '--add-data=icons:icons',
        '--hidden-import=skimage.filters.edges',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.scrolledtext',
        '--osx-bundle-identifier=com.clipimgfromvideo.slideextractor',
    ]
    
    # Add icon if available
    if icon_path and icon_path.endswith('.icns'):
        pyinstaller_args.append(f'--icon={icon_path}')
    
    # Add entry point
    pyinstaller_args.append('run_gui.py')
    
    print("Running PyInstaller with the following arguments:")
    print(" ".join(pyinstaller_args))
    
    try:
        subprocess.run(pyinstaller_args, check=True)
        
        # Create a simple README
        with open(os.path.join('dist', 'README.txt'), 'w') as f:
            f.write("""Presentation Slide Extractor

This application extracts slides from presentation videos.
Simply open the SlideExtractor app to start.

Features:
- Extract slides from local video files
- Extract videos from websites
- Save unique slides as images

For more information, visit: https://github.com/yourusername/clipimgfromvideo
""")
        
        print("\nBuild completed successfully!")
        app_path = os.path.abspath(os.path.join('dist', 'SlideExtractor.app'))
        print(f"The application is available at: {app_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        return False
    
    return True

if __name__ == '__main__':
    build_mac_app()
