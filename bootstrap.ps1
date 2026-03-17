# Bootstrap script for Windows PowerShell
param()

# Detect Python command
if (Get-Command py -ErrorAction SilentlyContinue) {
    $PY = 'py'
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PY = 'python3'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PY = 'python'
} else {
    Write-Error 'Python 3.7+ not found. Please install Python and add it to your PATH.'
    exit 1
}

Write-Output 'Creating virtual environment...'
& $PY -m venv .venv

Write-Output 'Activating virtual environment...'
. .\venv\Scripts\Activate.ps1

Write-Output 'Installing dependencies...'
pip install --upgrade pip
pip install --editable .

Write-Output ""
Write-Output 'Setup complete! 🎉'
Write-Output 'To run Budget Buddy, activate the venv and run:'
Write-Output '  budgetbuddy'
Write-Output 'or'
Write-Output '  py -3 -m budgetbuddy'
