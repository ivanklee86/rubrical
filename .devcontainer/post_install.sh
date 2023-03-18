#!/bin/bash
set -ex

# Configure poetry
WORKSPACE_DIR=$(pwd)
poetry config cache-dir ${WORKSPACE_DIR}/.cache
poetry config virtualenvs.in-project true
poetry self add "poetry-dynamic-versioning[plugin]"

# Intall dependencies
poetry install

# Install pre-config
pip install pre-commit
pre-commit install
pre-commit

# Configure git
git config --global --add --bool push.autoSetupRemote true

# Woohoo!
echo "Hooray, it's done!"
