#!/usr/bin/env sh

export server_path="/home/tarzan/Projects/pythoncad-optimizer/server/server.py"
export pyth="python3.6"

export cmd="${pyth} ${server_path}"

# replace the shell with a given program (executing it, not as new process)
exec $cmd
