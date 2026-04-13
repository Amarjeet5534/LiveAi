"""
Lightweight installer and launcher for LiveAI Desktop App
Handles environment setup and execution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_environment():
    """Create virtual environment and install dependencies"""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    
    # Determine pip executable
    pip_exe = venv_path / "Scripts" / "pip.exe" if os.name == 'nt' else venv_path / "bin" / "pip"
    python_exe = venv_path / "Scripts" / "python.exe" if os.name == 'nt' else venv_path / "bin" / "python"
    
    # Install requirements
    if (Path("requirements.txt")).exists():
        print("📥 Installing dependencies...")
        subprocess.run([str(pip_exe), "install", "-r", "requirements.txt", "--timeout=1000"], check=True)
    
    return str(python_exe)

def launch_app(python_exe):
    """Launch the desktop application"""
    print("🚀 Launching LiveAI Desktop App...")
    subprocess.run([python_exe, "desktop.py"])

if __name__ == "__main__":
    try:
        python_exe = setup_environment()
        launch_app(python_exe)
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
