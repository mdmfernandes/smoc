#!/usr/bin/env sh

pyth="python"

if echo "$("$pyth" -V 2>&1)" | grep -q "2."
then # If python is on version 2
    server_path="/home/mdm.fernandes/Projects/paim/server/server_py2.py"
else
    server_path="/home/mdm.fernandes/Projects/paim/server/server.py"
fi

cmd="${pyth} ${server_path}"

# replace the shell with a given program (executing it, not as new process)
exec $cmd
