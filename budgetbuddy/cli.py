import os
import sys
import subprocess

def main():
    """
    Entry point for Budget Buddy application.
    Launches the Streamlit app.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    app_path = os.path.join(here, "app.py")
    # Construct the command to run Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error launching Budget Buddy: {e}")
        sys.exit(1)
