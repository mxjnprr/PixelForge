#!/bin/bash
# Nano Banana Batch Processor - Linux Launcher
# Activates virtual environment if present and runs the application

cd "$(dirname "$0")"

# Check for virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check dependencies
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the application
echo "Starting Nano Banana Batch Processor..."
python3 main.py
