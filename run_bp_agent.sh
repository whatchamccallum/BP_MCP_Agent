#!/bin/bash

# Activate the virtual environment
source /path/to/your/venv/bin/activate

# Check if arguments are provided
if [ $# -eq 0 ]; then
  echo '{"result": "Please specify a command. Available commands: list-tests, run-test, report, charts, compare"}'
  exit 0
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Execute the command and capture output
output=$(python "$SCRIPT_DIR/main.py" "$@" 2>&1)

# Escape backslashes, double quotes, and newlines for proper JSON formatting
output=$(echo "$output" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')

# Output JSON
echo "{\"result\": \"$output\"}"
