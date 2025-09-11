import os
import subprocess
import sys
import venv

VENV_DIR = "venv"
MAIN_SCRIPT = "main.py"  # your entry point

# Required packages for the project
PACKAGES = [
    "PyQt5",
    "ollama",
    "watchdog",
    "pyinstaller"  # added
]

def run_command(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(result.returncode)

def create_venv():
    if not os.path.isdir(VENV_DIR):
        print(f"Creating virtual environment '{VENV_DIR}'...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
    else:
        print(f"Virtual environment '{VENV_DIR}' already exists.")

def install_packages():
    if os.name == "nt":
        pip_exec = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        pip_exec = os.path.join(VENV_DIR, "bin", "pip")

    # Install all packages
    for pkg in PACKAGES:
        run_command(f'"{pip_exec}" install {pkg}')

def run_main_script():
    if os.name == "nt":
        py_exec = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        py_exec = os.path.join(VENV_DIR, "bin", "python")
    run_command(f'"{py_exec}" {MAIN_SCRIPT}')

if __name__ == "__main__":
    create_venv()
    install_packages()
    run_main_script()
