#!/usr/bin/env bash
set -e

# Detect Python command
if command -v py &> /dev/null; then
  PY_CMD=py
elif command -v python3 &> /dev/null; then
  PY_CMD=python3
elif command -v python &> /dev/null; then
  PY_CMD=python
else
  echo "Python 3.7+ not found. Please install Python and add it to your PATH."
  exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
$PY_CMD -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install package
echo "Installing dependencies..."
pip install --upgrade pip
pip install --editable .

echo ""
echo "Setup complete! 🎉"
echo "To run Budget Buddy, activate the venv and run:"
echo "  budgetbuddy"
echo "or"
echo "  python -m budgetbuddy"
