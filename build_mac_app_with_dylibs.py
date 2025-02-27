"""
Build script for macOS that explicitly includes required dynamic libraries.
This addresses issues where macOS apps fail to launch due to missing dependencies.
"""
import os
import sys
import subprocess
import shutil
import platform
import site
import glob
from pathlib import Path
from app_icon import create_app_icon

def find_dylibs():
    """Find common dynamic libraries needed for video processing"""
    dylibs = []
    
    # Search for opencv dylibs
    cv2_paths = []
    
    # Try to find OpenCV libraries
    try:
        import cv2
        cv2_path = os.path.dirname(cv2.__file__)
        cv2_paths.append(cv2_path)
    except ImportError:
        print("Warning: OpenCV not found in current environment")
    
    # Add site-packages directories
    site_packages = site.getsitepackages()
    for sp in site_packages:
        cv_path = os.path.join(sp, 'cv2')
        if os.path.exists(cv_path):
            cv2_paths.append(cv_path)
    
    # Look for .dylib files in cv2 directories
    for path in cv2_paths:
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.dylib') or file.endswith('.so'):
                    full_path = os.path.join(root, file)
                    dylibs.append(full_path)
    
    # Also find NumPy, scikit-image dynamic libraries
    for lib in ['numpy', 'skimage', 'PIL', 'scipy']:
        try:
            package = __import__(lib)
            package_path = os.path.dirname(package.__file__)
            for root, _, files in os.walk(package_path):
                for file in files:
                    if file.endswith('.dylib') or file.endswith('.so'):
                        full_path = os.path.join(root, file)
                        dylibs.append(full_path)
        except (ImportError, AttributeError):
            print(f"Warning: {lib} not found or couldn't be searched")
    
    # If using yt-dlp, include its binaries
    try:
        import yt_dlp
        ytdlp_path = os.path.dirname(yt_dlp.__file__)
        for bin_path in glob.glob(os.path.join(ytdlp_path, "*.exe")) + glob.glob(os.path.join(ytdlp_path, "*.dylib")):
            dylibs.append(bin_path)
    except ImportError:
        print("Warning: yt-dlp not found")
    
    # Remove duplicates
    dylibs = list(set(dylibs))
    
    # Print found libraries
    if dylibs:
        print(f"Found {len(dylibs)} dynamic libraries to include:")
        for lib in dylibs[:5]:  # Show just first few to avoid cluttering output
            print(f" - {os.path.basename(lib)}")
        if len(dylibs) > 5:
            print(f" - ... and {len(dylibs) - 5} more")
    else:
        print("Warning: No dynamic libraries found to include")
        
    return dylibs

def build_mac_app():
    """Build macOS application bundle with explicit dynamic library includes"""
    if platform.system() != "Darwin":
        print("This script is intended for macOS only.")
        return False
    
    print("Starting build process for macOS application with explicit dylib includes...")
    
    # Create icon
    print("Creating application icon...")
    icon_path = create_app_icon()
    
    # Find dynamic libraries to include
    print("Finding required dynamic libraries...")
    dylibs = find_dylibs()
    
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
        
        # Explicitly collect all data files
        '--collect-all=cv2',
        '--collect-all=numpy',
        '--collect-all=skimage',
        '--collect-all=PIL',
        
        # Hidden imports for better compatibility
        '--hidden-import=skimage.filters.edges',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=PIL._imagingtk',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=numpy.core._dtype_ctypes',
        
        # Bundle metadata
        '--osx-bundle-identifier=com.clipimgfromvideo.slideextractor',
        
        # For better compatibility, use bundle mode not one-file
        '--noupx',  # Avoid UPX compression which can cause issues
    ]
    
    # Add icon if available
    if icon_path:
        pyinstaller_args.append(f'--icon={icon_path}')
        
    # Add binary dependencies as specified by the dylib search
    for dylib in dylibs:
        pyinstaller_args.append(f'--add-binary={dylib}:.')
    
    # Finally, add the entry point
    pyinstaller_args.append('run_gui.py')
    
    print("Running PyInstaller with the following arguments:")
    print(" ".join(pyinstaller_args[:10]) + "...")  # Just print the first few to avoid clutter
    
    try:
        # Run PyInstaller
        subprocess.run(pyinstaller_args, check=True)
        
        # Path to the app bundle
        app_path = os.path.abspath(os.path.join('dist', 'SlideExtractor.app'))
        
        # Make sure the executable is executable (sometimes permissions can get lost)
        executable_path = os.path.join(app_path, 'Contents', 'MacOS', 'SlideExtractor')
        if os.path.exists(executable_path):
            os.chmod(executable_path, 0o755)  # rwxr-xr-x
            print(f"Set executable permissions on {executable_path}")
            
        # Fix dylib permissions in the bundle
        for root, _, files in os.walk(app_path):
            for file in files:
                if file.endswith('.dylib') or file.endswith('.so'):
                    dylib_path = os.path.join(root, file)
                    os.chmod(dylib_path, 0o755)  # rwxr-xr-x
                    print(f"Set executable permissions on {os.path.basename(dylib_path)}")
        
        # Create a helper script for launching the app
        with open(os.path.join('dist', 'run_app.sh'), 'w') as f:
            f.write(f"""#!/bin/bash
# Helper script for launching the SlideExtractor app

# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
APP_PATH="$SCRIPT_DIR/SlideExtractor.app"

# Function to try different methods of launching the app
function try_open_app() {{
    echo "Trying to open the app..."
    if open -a "$APP_PATH"; then
        echo "App opened successfully!"
        return 0
    else
        echo "Failed to open app with 'open -a' command."
        return 1
    fi
}}

# Function to run the executable directly
function run_executable_directly() {{
    EXECUTABLE="$APP_PATH/Contents/MacOS/SlideExtractor"
    echo "Trying to run the executable directly: $EXECUTABLE"
    if [ -x "$EXECUTABLE" ]; then
        echo "Executable exists and has execute permissions."
        "$EXECUTABLE"
        return $?
    else
        echo "Executable doesn't exist or doesn't have execute permissions."
        return 1
    fi
}}

# Function to fix permissions
function fix_permissions() {{
    echo "Fixing permissions on the app bundle..."
    chmod -R u+x "$APP_PATH"
    find "$APP_PATH" -name "*.dylib" -exec chmod 755 {{}} \\;
    find "$APP_PATH" -name "*.so" -exec chmod 755 {{}} \\;
}}

# Main script
echo "Starting SlideExtractor helper script..."

if [ ! -d "$APP_PATH" ]; then
    echo "Error: SlideExtractor.app not found at $APP_PATH"
    exit 1
fi

# Fix permissions
fix_permissions

# Try to open normally
if try_open_app; then
    exit 0
fi

# If open failed, try running directly
echo "Attempting alternative launch method..."
run_executable_directly

exit $?
""")
        os.chmod(os.path.join('dist', 'run_app.sh'), 0o755)
        
        print("\nBuild completed successfully!")
        print(f"The application is available at: {app_path}")
        print("\nTo run the app, use the helper script:")
        print(f"bash {os.path.join('dist', 'run_app.sh')}")
        
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
