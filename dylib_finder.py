"""
Utility for finding dynamic libraries (.dylib, .so) used by the application.
This helps identify which libraries need to be explicitly included in the app bundle.
"""
import os
import sys
import subprocess
import platform
import importlib
import importlib.util
import site
from pathlib import Path


def find_module_path(module_name):
    """Find the path to a Python module"""
    try:
        module = importlib.import_module(module_name)
        return os.path.dirname(module.__file__)
    except (ImportError, AttributeError):
        return None


def find_dependencies(executable):
    """Find dependencies of an executable using otool"""
    if not os.path.exists(executable):
        print(f"Error: {executable} does not exist")
        return []
        
    try:
        result = subprocess.run(
            ['otool', '-L', executable],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract library paths from output
        lines = result.stdout.strip().split('\n')[1:]  # Skip first line which is the executable itself
        libraries = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Extract path, which should be the first part before any version or compatibility info
                path = line.split()[0]
                libraries.append(path)
                
        return libraries
    except subprocess.CalledProcessError as e:
        print(f"Error running otool: {e}")
        return []


def check_libraries(libraries):
    """Check if the libraries exist and are accessible"""
    missing = []
    for lib in libraries:
        if not os.path.exists(lib) and not lib.startswith('@'):
            missing.append(lib)
            
    return missing


def find_system_dylibs():
    """Find common system dynamic libraries used in video processing"""
    # Common system paths for libraries
    search_paths = [
        '/usr/lib',
        '/usr/local/lib',
        '/opt/homebrew/lib',  # Homebrew on M1 Macs
        '/usr/local/opt',     # Homebrew on Intel Macs
    ]
    
    # Libraries typically needed for video processing
    library_names = [
        'libopencv_*.dylib',
        'libavcodec*.dylib',
        'libavformat*.dylib',
        'libavutil*.dylib',
        'libswscale*.dylib',
        'libtiff*.dylib',
        'libjpeg*.dylib',
        'libpng*.dylib',
    ]
    
    found_libraries = []
    
    # Search for the libraries
    for path in search_paths:
        if os.path.exists(path):
            for name in library_names:
                pattern = os.path.join(path, name)
                for lib in Path(path).glob(name):
                    found_libraries.append(str(lib))
    
    return found_libraries


def analyze_python_modules():
    """Analyze key Python modules for their dynamic libraries"""
    modules_to_check = [
        'cv2',         # OpenCV
        'numpy',       # NumPy
        'skimage',     # scikit-image
        'PIL',         # Pillow
        'yt_dlp',      # YT-DLP
    ]
    
    results = {}
    
    for module_name in modules_to_check:
        module_path = find_module_path(module_name)
        if module_path:
            print(f"\nAnalyzing {module_name} at {module_path}")
            dylibs = []
            
            # Find all .so and .dylib files
            for root, _, files in os.walk(module_path):
                for file in files:
                    if file.endswith('.dylib') or file.endswith('.so'):
                        full_path = os.path.join(root, file)
                        dylibs.append(full_path)
                        
                        # Get dependencies for this library
                        deps = find_dependencies(full_path)
                        missing = check_libraries(deps)
                        
                        if missing:
                            print(f"  {file} has missing dependencies:")
                            for lib in missing:
                                print(f"    - {lib}")
            
            if dylibs:
                print(f"  Found {len(dylibs)} libraries")
                results[module_name] = dylibs
            else:
                print("  No libraries found")
        else:
            print(f"{module_name} not found")
    
    return results


def main():
    """Main function"""
    if platform.system() != "Darwin":
        print("This script is for macOS only")
        return
        
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"macOS version: {platform.mac_ver()[0]}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python version: {platform.python_version()}")
    
    print("\nChecking Python executable dependencies:")
    python_deps = find_dependencies(sys.executable)
    missing = check_libraries(python_deps)
    
    if missing:
        print("Missing libraries for Python executable:")
        for lib in missing:
            print(f"  - {lib}")
            
    print("\nAnalyzing Python modules...")
    module_results = analyze_python_modules()
    
    # Generate PyInstaller binary-includes commands
    print("\nPyInstaller --add-binary commands for found libraries:")
    for module, libs in module_results.items():
        for lib in libs:
            print(f"--add-binary={lib}:.")
    
    # Look for system libraries
    print("\nSearching for system libraries that might be needed...")
    system_libs = find_system_dylibs()
    if system_libs:
        print(f"Found {len(system_libs)} potentially useful system libraries.")
        print("To include these in your app bundle, add these PyInstaller arguments:")
        for lib in system_libs[:5]:  # Show just first 5
            print(f"--add-binary={lib}:.")
        if len(system_libs) > 5:
            print(f"... and {len(system_libs) - 5} more")
    
    print("\nTo fix missing library issues, try the following:")
    print("1. Build with new script: python build_mac_app_with_dylibs.py")
    print("2. Use the helper script: bash dist/run_app.sh")


if __name__ == "__main__":
    main()
