#!/usr/bin/env sh

# Project name
export PROJECT_NAME="teste1"

# Paths
export SCRIPT_PATH="/home/tarzan/Projects/$PROJECT_NAME/script"
export RESULT_PATH="/home/tarzan/Projects/$PROJECT_NAME/sim-results"


export server_path="/home/tarzan/Projects/pythoncad-optimizer/server/server.py"
export pyth="python3.6"

export cmd="${pyth} ${server_path}"

# replace the shell with a given program (executing it, not as new process)
exec $cmd
