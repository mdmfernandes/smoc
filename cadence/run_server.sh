#!/usr/bin/env sh

pyth="python"

server_path="/home/mdm.fernandes/Projects/paim/server/server.py"

cmd="${pyth} ${server_path}"

# replace the shell with a given program (executing it, not as new process)
exec $cmd
