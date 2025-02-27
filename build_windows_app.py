"""
Build script for creating a standalone Windows executable using PyInstaller.
"""
import os
import sys
import subprocess
import shutil
from app_icon import create_app_icon

def build_windows_app():
    """Build the Windows standalone executable"""
    print("Starting build process for Windows executable...")
    
    # Create icon if it doesn't exist
    icon_path = os.path.join('icons', 'app_icon.ico')
    if not os.path.exists(icon_path):
        print("Creating application icon...")
        create_app_icon()
    
    # Ensure the dist directory is clean
    if os.path.exists('dist'):
        print("Cleaning previous build...")
        shutil.rmtree('dist')
    
    # Determine platform-specific separator for --add-data
    # Windows uses semicolon (;), macOS/Linux uses colon (:)
    separator = ';' if sys.platform.startswith('win') else ':'
    
    # Prepare PyInstaller command
    pyinstaller_args = [
        'pyinstaller',
        '--name=SlideExtractor',
        '--onefile',
        f'--icon={icon_path}',
        '--windowed',  # No console window
        f'--add-data=icons{separator}icons',  # Add icon folder with platform-specific separator
        '--hidden-import=skimage.filters.edges',  # Required for scikit-image
        '--hidden-import=PIL._tkinter_finder',  # For PIL/Tkinter integration
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.scrolledtext',
        'run_gui.py'  # Entry point script
    ]
    
    # Run PyInstaller
    print("Running PyInstaller with the following arguments:")
    print(" ".join(pyinstaller_args))
    
    try:
        subprocess.run(pyinstaller_args, check=True)
        
        # Create a simple README in the dist folder
        with open(os.path.join('dist', 'README.txt'), 'w') as f:
            f.write("""Presentation Slide Extractor

This application extracts slides from presentation videos.
Simply run SlideExtractor.exe to start.

Features:
- Extract slides from local video files
- Extract videos from websites
- Save unique slides as images

For more information, visit: https://github.com/yourusername/clipimgfromvideo
""")
            
        print("\nBuild completed successfully!")
        print(f"The executable is available at: {os.path.abspath(os.path.join('dist', 'SlideExtractor.exe'))}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        return False
    
    return True

if __name__ == '__main__':
    build_windows_app()
