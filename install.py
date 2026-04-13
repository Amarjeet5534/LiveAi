"""
LiveAI Desktop App - Windows Installer
One-click setup and installation
"""

import os
import sys
import subprocess
import shutil
import urllib.request
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python():
    """Verify Python version"""
    print("🐍 Checking Python installation...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} found")
    return True

def setup_venv():
    """Create and activate virtual environment"""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return venv_path
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created")
        return venv_path
    except Exception as e:
        print(f"❌ Failed to create venv: {e}")
        return None

def install_deps():
    """Install Python dependencies"""
    print("📥 Installing dependencies (this may take 5-10 minutes)...")
    
    pip_exe = Path(".venv") / "Scripts" / "pip.exe"
    
    try:
        subprocess.run(
            [str(pip_exe), "install", "-r", "requirements.txt", "--timeout=1000"],
            check=True
        )
        print("✅ Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_ollama():
    """Check if Ollama is running"""
    print("🤖 Checking Ollama service...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 11434))
        sock.close()
        
        if result == 0:
            print("✅ Ollama is running on port 11434")
            return True
        else:
            print("⚠️  Ollama is NOT running on port 11434")
            print("   Download from: https://ollama.ai")
            print("   Then run: ollama pull phi3")
            return False
    except Exception as e:
        print(f"⚠️  Could not check Ollama: {e}")
        return False

def create_shortcuts():
    """Create desktop shortcuts"""
    print("📌 Creating shortcuts...")
    
    desktop = Path.home() / "Desktop"
    
    # Create batch file shortcut
    bat_content = """@echo off
cd /d "%~dp0LiveAI"
call .venv\\Scripts\\activate.bat
python desktop.py
pause
"""
    
    bat_path = desktop / "Start LiveAI.bat"
    try:
        with open(bat_path, 'w') as f:
            f.write(bat_content)
        print(f"✅ Created shortcut: {bat_path}")
    except Exception as e:
        print(f"⚠️  Could not create shortcut: {e}")

def main():
    print_header("LiveAI Desktop App - Installation Wizard")
    
    # Check Python
    if not check_python():
        print("\n❌ Installation failed. Please install Python 3.9 or newer.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Setup venv
    print()
    if not setup_venv():
        print("\n❌ Installation failed.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Install dependencies
    print()
    if not install_deps():
        print("\n⚠️  Some dependencies failed. The app may not work correctly.")
    
    # Check Ollama
    print()
    check_ollama()
    
    # Create shortcuts
    print()
    create_shortcuts()
    
    # Summary
    print_header("✅ Installation Complete!")
    print("""
To start LiveAI Desktop App, run:
  1. Double-click LiveAI.bat in the project folder
  2. Or run: python launcher.py
  3. Or run: python desktop.py

Login with:
  Username: admin
  Password: admin123

📖 For more help, see DESKTOP_DEPLOYMENT.md
    """)
    
    # Offer to launch app
    response = input("\nWould you like to launch the app now? (y/n): ").lower()
    if response == 'y':
        python_exe = Path(".venv") / "Scripts" / "python.exe"
        subprocess.run([str(python_exe), "desktop.py"])
    else:
        print("\nSetup complete! Goodbye.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
