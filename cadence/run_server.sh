#!/usr/bin/env sh

# TODO: IF python -V == 2,
#export server_path="/home/mdm.fernandes/Projects/paim/server/server_py2.py"

export server_path="/home/mdm.fernandes/Projects/paim/server/server.py"
export pyth="python"

export cmd="${pyth} ${server_path}"

# replace the shell with a given program (executing it, not as new process)
exec $cmd
