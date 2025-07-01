#!/bin/bash

# Get the directory of this script, handling spaces correctly
SCRIPT_PATH="/Users/diegoaguirre/instagram automation/launch_batch_manager.sh"
SCRIPT_DIR="/Users/diegoaguirre/instagram automation"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Launch the GUI using absolute path
python3 "$SCRIPT_DIR/batch_follow_gui.py" 