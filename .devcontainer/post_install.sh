#!/bin/bash
set -ex

# Configure poetry
WORKSPACE_DIR=$(pwd)
poetry config cache-dir ${WORKSPACE_DIR}/.cache
poetry config virtualenvs.in-project true

# Intall dependencies
poetry install

# Woohoo!
echo "Hooray, it's done!"
