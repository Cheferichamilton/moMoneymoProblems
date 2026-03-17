# Budget Buddy

A simple budgeting tool with pay schedule and recurring bills, powered by Streamlit.

## Prerequisites

- Python 3.7+ installed on your system.
- On Windows, be sure to check "Add Python to PATH" during installation so that `python`, `pip`, or `py` commands are recognized.
- If these commands are not available, reinstall Python from https://python.org or adjust your PATH environment variable.

## Installation

After cloning the repo, run the appropriate bootstrap script to set up a virtual environment and install dependencies:

On macOS/Linux:
```bash
./bootstrap.sh
```

On Windows PowerShell:
```powershell
.\bootstrap.ps1
```

Once complete, activate the virtual environment and run:
```bash
budgetbuddy
# or
python -m budgetbuddy
```

Install directly from GitHub:

On macOS/Linux:
```bash
pip install --user git+https://github.com/Cheferichamilton/moMoneymoProblems.git
```

On Windows PowerShell or CMD:
```powershell
# If you have the Python launcher installed:
py -3 -m pip install --user git+https://github.com/Cheferichamilton/moMoneymoProblems.git
# Or if `py` isn't available but `python` is in your PATH:
python -m pip install --user git+https://github.com/Cheferichamilton/moMoneymoProblems.git
```

After install, in the same shell:
```powershell
# To run Budget Buddy:
py -3 -m budgetbuddy
# Or if you installed entry script and it's on PATH:
budgetbuddy
```

## VSCode Setup

If you’re using VSCode, follow these steps for smooth sailing:

1. Open the VSCode Command Palette (Ctrl+Shift+P) and choose **Python: Select Interpreter**. Select the `.venv` interpreter we just created.
2. Open the integrated terminal (Ctrl+`) and ensure your prompt shows `(venv)`.
   - If not active, run:
     - On Windows: `.\\venv\\Scripts\\Activate.ps1`
     - On macOS/Linux: `source .venv/bin/activate`
3. In the same integrated terminal, run:
   ```bash
   python -m budgetbuddy
   ```

This will start your Streamlit app within the VSCode terminal environment.

## Usage

Open any terminal (macOS/Linux, Windows PowerShell, CMD, or VSCode integrated terminal). Then run:

```bash
budgetbuddy
```

If `budgetbuddy` isn't recognized (common on Windows), use:

```bash
python -m budgetbuddy
```

Either will launch the Streamlit UI in your browser.

## Updating

To get the latest version:

```bash
pip install --upgrade --user git+https://github.com/Cheferichamilton/moMoneymoProblems.git
```

## Requirements

- Python 3.7+
- SQLite (built-in Python)

Enjoy budgeting with Budget Buddy! 🎉🐶
