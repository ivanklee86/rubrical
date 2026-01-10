# See here for image contents: https://github.com/microsoft/vscode-dev-containers/blob/main/containers/go/.devcontainer/Dockerfile
ARG BASE="debian-12"
FROM mcr.microsoft.com/devcontainers/base:${BASE}

# Setup
ENV HOME="/home/vscode"
WORKDIR /home/vscode

USER vscode

# Install and configure Python
ENV UV_CACHE_DIR="/home/vscode/.uv_cache"
COPY --from=ghcr.io/astral-sh/uv:debian /usr/local/bin/uv /usr/local/bin
COPY --from=ghcr.io/astral-sh/uv:debian /usr/local/bin/uvx /usr/local/bin
ARG PYTHON_VERSION=3.14
RUN uv python install ${PYTHON_VERSION}
ENV UV_LINK_MODE=copy

# Install tools
# - Tools
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
