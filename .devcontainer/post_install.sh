#!/bin/bash
set -ex

# Install dependencies (prek hooks are installed by the install-prek postCreateCommand)
uv sync --group dev

# Configure git
if [ "$CODESPACES" != "true" ]; then
    echo "Running locally, configure gpg."

    git config --global gpg.program gpg2
    git config --global commit.gpgsign true
else
    echo "Running in codespaces."
fi

git config --global --add --bool push.autoSetupRemote true

# Woohoo!
echo "Hooray, it's done!"
