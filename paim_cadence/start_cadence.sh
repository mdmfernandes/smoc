#!/usr/bin/env sh
# This file is part of PAIM
# Copyright (C) 2018 Miguel Fernandes
#
# PAIM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PAIM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Project name
export PAIM_PROJECT_NAME="commonSource-tutorial"
# Project work space
PAIM_WORK_SPACE="/home/mdm.fernandes/Projects"

## Server info
# Client Address
export PAIM_CLIENT_ADDR="localhost"
# Client Port
export PAIM_CLIENT_PORT="3000"


#############################################
#       Do not change the code below!       #
#############################################
# DefinepPaths
export PAIM_ROOT_DIR="$PAIM_WORK_SPACE/$PAIM_PROJECT_NAME"
export PAIM_SCRIPT_DIR="$PAIM_ROOT_DIR/script"

# Create the root dir, if it doesn't exist
if [ ! -d "$PAIM_ROOT_DIR" ]; then
    echo
    echo "[INFO] Creating $PAIM_ROOT_DIR ..."
    mkdir $PAIM_ROOT_DIR
    cp -r script/ $PAIM_ROOT_DIR # Copy the script folder to the project folder
else
    echo
    echo "[INFO] The directory $PAIM_ROOT_DIR already exists."
fi

# Create the results file in the project root directory
touch "$PAIM_ROOT_DIR/sim_res"

echo
echo "**********************************************************************"
echo "*                          Starting Cadence                          *"
echo "**********************************************************************"
# Code to run Cadence and the script cadence.il
virtuoso -nograph -restore cadence.il
