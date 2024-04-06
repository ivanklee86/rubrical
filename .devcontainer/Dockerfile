
# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3.12
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# [CHOICE] Poetry version: v1.2.2, etc
ARG POETRY_VERSION="none"
RUN if [ "${POETRY_VERSION}" != "none" ]; then su vscode -c "umask 0002 && pipx install poetry==${POETRY_VERSION}"; fi

# Update pip
RUN pip install -U pip

# Install task
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d

# Git configure
RUN git config --global push.autoSetupRemote true

ENV PATH="$HOME/.venv/bin:$PATH"
