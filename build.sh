#!/usr/bin/env bash
set -euo pipefail

# debug
echo "Python:" $(python -V)
echo "Pip:" $(pip -V)

# ensure pip can install binary wheels where available
pip install --upgrade pip setuptools wheel

# force cargo/rust to use writable paths (Render's /tmp is writable)
export CARGO_HOME=/tmp/.cargo
export RUSTUP_HOME=/tmp/.rustup
export CARGO_TARGET_DIR=/tmp/.cargo-target

# prefer prebuilt binary wheels when available (faster & avoids building)
pip install --prefer-binary -r requirements.txt
