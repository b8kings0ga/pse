"""
Improved build script for creating a macOS application bundle.
Includes fixes for common issues that prevent apps from opening.
"""
import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from app_icon import create_app_icon

def build_mac_app():
    """Build an improved macOS application bundle"""
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
    
    # Improved PyInstaller arguments for better compatibility
    pyinstaller_args = [
        'pyinstaller',
        '--name=SlideExtractor',
        '--windowed',  # Create a .app bundle
        '--add-data=icons:icons',
        
        # Hidden imports for better compatibility
        '--hidden-import=skimage.filters.edges',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=PIL._imagingtk',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=tkinter.ttk',
        
        # Fix for Numpy
        '--hidden-import=numpy.core._dtype_ctypes',
        
        # Bundle metadata
        '--osx-bundle-identifier=com.clipimgfromvideo.slideextractor',
        
        # For better compatibility, avoid onefile mode which has more issues on macOS
        # '--onefile',
    ]
    
    # Add icon if available
    if icon_path and (icon_path.endswith('.icns') or icon_path.endswith('.png')):
        pyinstaller_args.append(f'--icon={icon_path}')
    
    # Add entry point
    pyinstaller_args.append('run_gui.py')
    
    print("Running PyInstaller with the following arguments:")
    print(" ".join(pyinstaller_args))
    
    try:
        # Run PyInstaller
        subprocess.run(pyinstaller_args, check=True)
        
        # Path to the app bundle
        app_path = os.path.abspath(os.path.join('dist', 'SlideExtractor.app'))
        
        # Make sure the executable is executable (sometimes permissions can get lost)
        executable_path = os.path.join(app_path, 'Contents', 'MacOS', 'SlideExtractor')
        if os.path.exists(executable_path):
            os.chmod(executable_path, 0o755)  # rwxr-xr-x
            
        # Create a README
        with open(os.path.join('dist', 'README.txt'), 'w') as f:
            f.write("""Presentation Slide Extractor

This application extracts slides from presentation videos.
Simply open the SlideExtractor app to start.

If the app doesn't open:
1. Try running it from the terminal: open -a SlideExtractor.app
2. Remove quarantine attribute: xattr -d com.apple.quarantine SlideExtractor.app
3. Check Console.app for crash logs

Features:
- Extract slides from local video files
- Extract videos from websites
- Save unique slides as images

For more information, visit: https://github.com/yourusername/clipimgfromvideo
""")
        
        # Create a shell script to help with opening the app
        with open(os.path.join('dist', 'open_app.sh'), 'w') as f:
            f.write(f"""#!/bin/bash
# Script to help open the SlideExtractor app
# This can sometimes help bypass macOS security restrictions

# Remove quarantine attribute if present
xattr -d com.apple.quarantine "{app_path}" 2>/dev/null

# Open the app
open -a "{app_path}"

# If that didn't work, try running the executable directly
if [ $? -ne 0 ]; then
    echo "Failed to open app with 'open' command. Trying direct execution..."
    "{executable_path}"
fi
""")
        os.chmod(os.path.join('dist', 'open_app.sh'), 0o755)
        
        print("\nBuild completed successfully!")
        print(f"The application is available at: {app_path}")
        print("\nIf the app doesn't open, try running the following command:")
        print(f"bash {os.path.join('dist', 'open_app.sh')}")
        print("\nOr try removing the quarantine attribute:")
        print(f"xattr -d com.apple.quarantine {app_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        return False
    
    # Run the diagnostic tool
    try:
        print("\nRunning diagnostic checks on the app bundle...")
        subprocess.run(["python", "mac_app_diagnostics.py", app_path], check=False)
    except Exception as e:
        print(f"Error running diagnostics: {e}")
    
    return True

if __name__ == '__main__':
    build_mac_app()
