#!/bin/bash
# Daily runner for Poem Short Generator 2
# Schedules: set via cron (see README)

set -euo pipefail

PROJECT_DIR="/Users/peterhagen/Desktop/poem-short-generator-2"
PYTHON_BIN="python"  # change to your venv python if needed, e.g., "$PROJECT_DIR/.venv/bin/python"
LOG_FILE="$PROJECT_DIR/cron.log"

cd "$PROJECT_DIR"

# Activate virtualenv if you use one
# source "$PROJECT_DIR/.venv/bin/activate"

# Run the pipeline (7 stanzas, poetic insight tone). Adjust flags as desired.
TZ=America/New_York $PYTHON_BIN main.py --stanzas 7 --tone "poetic insight" >> "$LOG_FILE" 2>&1

# Point output/latest to the newest run
latest_dir=$(ls -dt "$PROJECT_DIR"/output/* 2>/dev/null | head -1 || true)
if [ -n "$latest_dir" ]; then
  ln -sfn "$latest_dir" "$PROJECT_DIR/output/latest"
fi


