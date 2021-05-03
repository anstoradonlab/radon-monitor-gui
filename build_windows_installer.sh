#!/bin/bash
#
# build windows app
#

# create minimal environment to get the right version of Python

if [[ ! -d ./env ]]
then
    conda create --prefix ./minenv
fi

conda env update --prefix ./minenv --file minimal-env.yml  --prune

# create a virtual environment and install dependencies using pip

python -m venv venv
pip install -r requirements/windows.txt

# debug/release build
fbs freeze --debug
#fbs freeze

# installer
fbs installer