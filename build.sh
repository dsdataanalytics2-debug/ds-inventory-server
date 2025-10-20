#!/usr/bin/env bash
set -euo pipefail

# upgrade pip & helpers first
pip install --upgrade pip setuptools wheel

# avoid cargo writing to readonly paths
export CARGO_HOME=/tmp/.cargo
export RUSTUP_HOME=/tmp/.rustup
export CARGO_TARGET_DIR=/tmp/.cargo-target

# install requirements, prefer prebuilt binaries
pip install --prefer-binary -r requirements.txt
