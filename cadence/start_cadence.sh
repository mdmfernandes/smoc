#!/usr/bin/env sh

# Project name
export PROJECT_NAME="commonSource-tutorial"
# Project root directory
WORK_SPACE="/home/mdm.fernandes/Projects"

## Server info
# Client Address
export CLIENT_ADDR="localhost"
# Client Port
export CLIENT_PORT="3000"

#############################################
#       Do not change the code below!       #
#############################################

# Get current date (format: yyyymmdd-hhmmss)
NOW=$(date +"%Y%m%d_%H-%M-%S")

# Paths
ROOT_DIR="$WORK_SPACE/$PROJECT_NAME"
export SCRIPT_PATH="$ROOT_DIR/script"
export VAR_PATH="$ROOT_DIR/$NOW/var"
export RESULT_PATH="$ROOT_DIR/$NOW/sim"

# Create the root dir, if it doesn't exist
if [ ! -d "$ROOT_DIR" ]; then
    echo "*INFO* Creating $ROOT_DIR ..."
    mkdir $ROOT_DIR
    cp -r script/ $ROOT_DIR
else
    echo "*INFO* The directory $ROOT_DIR already exists."
fi

# Create the session directory 
# Everytime this script is executed, a new dir is created (to mantain old files)
mkdir "$ROOT_DIR/$NOW"

# Create the dir circuit-vars, if it doesn't exist
if [ ! -d "$VAR_PATH" ]; then
    echo "*INFO* Creating $VAR_PATH ..."
    mkdir $VAR_PATH   
else    # If dir exists, delete the content
    rm $VAR_PATH/*
fi

# Create the dir sim-results, if it doesn't exist
if [ ! -d "$RESULT_PATH" ]; then
    echo "*INFO* Creating $RESULT_PATH ..."
    mkdir $RESULT_PATH
else    # If dir exists, delete the content
    rm $RESULT_PATH/*
fi

echo
echo "**********************************************************************"
echo "*                          Starting Cadence                          *"
echo "**********************************************************************"
# Code to run Cadence and the script cadence.il
virtuoso -nograph -restore cadence.il
