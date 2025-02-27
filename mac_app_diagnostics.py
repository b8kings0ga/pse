"""
Diagnostic utility for macOS app bundles.
Helps identify common issues preventing app launch.
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            shell=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"stderr: {e.stderr}")
        return None


def diagnose_app(app_path):
    """Run diagnostics on a macOS app bundle"""
    print(f"Diagnosing app bundle: {app_path}")
    
    if not os.path.exists(app_path):
        print("Error: App bundle does not exist!")
        return
        
    if not app_path.endswith('.app'):
        print("Warning: Path doesn't look like an app bundle (.app extension missing)")
        
    # Check macOS version
    mac_ver = platform.mac_ver()[0]
    print(f"macOS version: {mac_ver}")
    
    # Check architecture
    arch = platform.machine()
    print(f"System architecture: {arch}")
    
    # Check if the app bundle has the basic structure
    contents_path = os.path.join(app_path, "Contents")
    if not os.path.exists(contents_path):
        print("Error: Invalid app bundle structure (Contents directory missing)")
        return
        
    macos_path = os.path.join(contents_path, "MacOS")
    if not os.path.exists(macos_path):
        print("Error: Invalid app bundle structure (MacOS directory missing)")
        return
        
    # Find the executable
    executables = [f for f in os.listdir(macos_path) if os.path.isfile(os.path.join(macos_path, f))]
    if not executables:
        print("Error: No executable found in MacOS directory")
        return
        
    executable_path = os.path.join(macos_path, executables[0])
    print(f"Executable found: {executables[0]}")
    
    # Check executable permissions
    if not os.access(executable_path, os.X_OK):
        print("Error: Executable does not have execution permission")
    else:
        print("Executable has proper permissions")
        
    # Check code signing
    print("\nCode signing information:")
    signing_info = run_command(f"codesign -dvv '{app_path}' 2>&1")
    print(signing_info or "No signing information available")
    
    # Check for quarantine attribute
    print("\nChecking for quarantine attribute:")
    quarantine = run_command(f"xattr -l '{app_path}' | grep quarantine")
    if quarantine:
        print(f"Quarantine attribute found: {quarantine}")
        print("Try removing quarantine attribute with:")
        print(f"xattr -d com.apple.quarantine '{app_path}'")
    else:
        print("No quarantine attribute found")
    
    # Try running the executable directly for error messages
    print("\nAttempting to run the executable directly:")
    try:
        result = subprocess.run(
            executable_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            timeout=2  # Set a short timeout
        )
        print("Executable ran without immediate errors")
    except subprocess.TimeoutExpired:
        print("Executable started (timeout after 2 seconds as expected)")
    except subprocess.SubprocessError as e:
        print(f"Error running executable: {e}")
    
    # Check for common issues in the Info.plist
    info_plist = os.path.join(contents_path, "Info.plist")
    if os.path.exists(info_plist):
        print("\nChecking Info.plist:")
        plist_content = run_command(f"plutil -p '{info_plist}'")
        if plist_content:
            print("Info.plist looks valid")
            
            # Check for specific keys
            bundle_id = run_command(f"defaults read '{info_plist}' CFBundleIdentifier")
            if bundle_id:
                print(f"Bundle ID: {bundle_id.strip()}")
            
            executable_name = run_command(f"defaults read '{info_plist}' CFBundleExecutable")
            if executable_name:
                print(f"Executable name in plist: {executable_name.strip()}")
                if executable_name.strip() != executables[0]:
                    print("Warning: Executable name in Info.plist doesn't match actual executable")
    else:
        print("Error: Info.plist not found")
    
    # Check dynamic library dependencies
    print("\nChecking dynamic library dependencies:")
    libs = run_command(f"otool -L '{executable_path}'")
    if libs:
        print(libs)
    
    # Give recommendations
    print("\nRecommendations:")
    print("1. Try running the app from the terminal with:")
    print(f"   open -a '{app_path}'")
    print("2. Check Console.app for crash reports related to the app")
    print("3. If the app is from the internet, remove quarantine attribute:")
    print(f"   xattr -d com.apple.quarantine '{app_path}'")
    print("4. Try rebuilding with explicit dylib includes")


if __name__ == "__main__":
    if platform.system() != "Darwin":
        print("This script is for macOS only")
        sys.exit(1)
        
    if len(sys.argv) > 1:
        app_path = sys.argv[1]
    else:
        app_path = os.path.abspath("dist/SlideExtractor.app")
        
    diagnose_app(app_path)
