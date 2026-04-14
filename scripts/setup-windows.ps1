# Virtual Chief of Staff - Windows Setup script
# This script automates the installation of 'uv' and 'ffmpeg' using winget.

$ErrorActionPreference = "Stop"

Write-Host "🔍 Starting Virtual Chief of Staff environment setup..." -ForegroundColor Cyan

# 1. Check/Install winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Error "winget not found. Please install App Installer from the Microsoft Store."
    exit 1
}

# 2. Install uv (Astral-sh)
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing 'uv' (Python package manager)..." -ForegroundColor Yellow
    winget install --id=astral-sh.uv -e --accept-source-agreements --accept-package-agreements --silent
    Write-Host "✅ 'uv' installed." -ForegroundColor Green
} else {
    Write-Host "✅ 'uv' is already installed." -ForegroundColor Green
}

# 3. Install FFmpeg (required for local transcription)
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing 'FFmpeg' (for audio transcription)..." -ForegroundColor Yellow
    winget install --id=Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements --silent
    Write-Host "✅ 'FFmpeg' installed." -ForegroundColor Green
} else {
    Write-Host "✅ 'FFmpeg' is already installed." -ForegroundColor Green
}

# 4. Success message
Write-Host "`n✨ Core dependencies are ready!" -ForegroundColor Cyan
Write-Host "Tip: You may need to RESTART your terminal/Claude Code to pick up the new paths." -ForegroundColor White
Write-Host "Once restarted, run: uv tool install vcos" -ForegroundColor White
