# CIG-APP / GOAT-TS low-end setup for Windows
$ErrorActionPreference = "Stop"
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt
Write-Host "Ensuring Rust toolchain..."
rustup install stable 2>$null; if (-not $?) { Write-Host "Rustup not in PATH or failed - install from https://rustup.rs" }
Write-Host "Building Rust extension..."
try { cargo build --manifest-path=rust/Cargo.toml } catch { Write-Host "Rust build skipped (run after Step 3)" }
Write-Host "Setup complete."
