"""
Cross-platform build script for creating standalone executables using PyInstaller.
This script automatically detects the current platform and uses appropriate settings.
"""
import os
import sys
import subprocess
import shutil
import platform
from app_icon import create_app_icon

def build_app():
    """Build the standalone executable for the current platform"""
    current_platform = platform.system()
    print(f"Starting build process for {current_platform} executable...")
    
    # Create icon if it doesn't exist
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
    
    # Determine platform-specific settings
    separator = ';' if current_platform == "Windows" else ':'
    
    # Common PyInstaller arguments
    pyinstaller_args = [
        'pyinstaller',
        '--name=SlideExtractor',
        '--onefile',
        '--windowed',  # No console window
        f'--add-data=icons{separator}icons',  # Add icon folder with platform-specific separator
        '--hidden-import=skimage.filters.edges',  # Required for scikit-image
        '--hidden-import=PIL._tkinter_finder',  # For PIL/Tkinter integration
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.scrolledtext',
    ]
    
    # Add icon if available
    if icon_path:
        pyinstaller_args.append(f'--icon={icon_path}')
    
    # Add entry point script
    pyinstaller_args.append('run_gui.py')
    
    # Platform-specific additions
    if current_platform == "Darwin":  # macOS
        pyinstaller_args.extend([
            '--osx-bundle-identifier=com.clipimgfromvideo.slideextractor',
        ])
        
        # Only add universal2 if on an arm64 Mac with PyInstaller that supports it
        # This is to avoid errors on older PyInstaller versions or Intel Macs
        try:
            if subprocess.run(['arch'], stdout=subprocess.PIPE).stdout.decode().strip() == 'arm64':
                pyinstaller_args.append('--target-architecture=universal2')
        except:
            pass
    
    # Run PyInstaller
    print("Running PyInstaller with the following arguments:")
    print(" ".join(pyinstaller_args))
    
    try:
        subprocess.run(pyinstaller_args, check=True)
        
        # Create a simple README in the dist folder
        with open(os.path.join('dist', 'README.txt'), 'w') as f:
            f.write("""Presentation Slide Extractor

This application extracts slides from presentation videos.
Simply run the application to start.

Features:
- Extract slides from local video files
- Extract videos from websites
- Save unique slides as images

For more information, visit: https://github.com/yourusername/clipimgfromvideo
""")
            
        print("\nBuild completed successfully!")
        
        # Show location of the executable based on platform
        if current_platform == "Windows":
            exe_path = os.path.abspath(os.path.join('dist', 'SlideExtractor.exe'))
        elif current_platform == "Darwin":
            exe_path = os.path.abspath(os.path.join('dist', 'SlideExtractor.app'))
        else:
            exe_path = os.path.abspath(os.path.join('dist', 'SlideExtractor'))
            
        print(f"The executable is available at: {exe_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        # Try again without windowed mode for easier debugging
        print("Retrying with console window for debugging...")
        if '--windowed' in pyinstaller_args:
            pyinstaller_args.remove('--windowed')
            
        try:
            subprocess.run(pyinstaller_args, check=True)
            print("\nBuild completed with console mode.")
        except subprocess.CalledProcessError as e:
            print(f"Second build attempt failed: {e}")
            return False
    
    return True

if __name__ == '__main__':
    build_app()
