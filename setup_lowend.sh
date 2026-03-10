#!/bin/bash
set -e
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "Ensuring Rust toolchain..."
rustup install stable 2>/dev/null || true
echo "Building Rust extension..."
cargo build --manifest-path=rust/Cargo.toml 2>/dev/null || echo "Rust build skipped (run after Step 3)"
echo "Setup complete."
