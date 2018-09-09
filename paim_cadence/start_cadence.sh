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
# Get current date (format: yyyymmdd_hh-mm-ss)
NOW=$(date +"%Y%m%d_%H-%M-%S")

# Paths
ROOT_DIR="$PAIM_WORK_SPACE/$PAIM_PROJECT_NAME"
export PAIM_SCRIPT_PATH="$ROOT_DIR/script"
export PAIM_VAR_PATH="$ROOT_DIR/$NOW/var"
export PAIM_RESULT_PATH="$ROOT_DIR/$NOW/sim"

# Create the root dir, if it doesn't exist
if [ ! -d "$ROOT_DIR" ]; then
    echo "[INFO] Creating $ROOT_DIR ..."
    mkdir $ROOT_DIR
    cp -r script/ $ROOT_DIR # Copy the script folder to the project folder
else
    echo "[INFO] The directory $ROOT_DIR already exists."
fi

# Create the session directory 
# Everytime this script is executed, a new dir is created (to mantain old files)
mkdir "$ROOT_DIR/$NOW"

# Create the dir circuit-vars, if it doesn't exist
if [ ! -d "$PAIM_VAR_PATH" ]; then
    echo "[INFO] Creating $PAIM_VAR_PATH ..."
    mkdir $PAIM_VAR_PATH   
else    # If dir exists, delete the content
    rm $PAIM_VAR_PATH/*
fi

# Create the dir sim-results, if it doesn't exist
if [ ! -d "$PAIM_RESULT_PATH" ]; then
    echo "[INFO] Creating $PAIM_RESULT_PATH ..."
    mkdir $PAIM_RESULT_PATH
else    # If dir exists, delete the content
    rm $PAIM_RESULT_PATH/*
fi

echo
echo "**********************************************************************"
echo "*                          Starting Cadence                          *"
echo "**********************************************************************"
# Code to run Cadence and the script cadence.il
virtuoso -nograph -restore cadence.il
