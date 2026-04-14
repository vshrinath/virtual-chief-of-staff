# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2026-04-14] — Self-Documenting Help System & Integration Helpers

**Branch**: `main`

### What changed
- **`vcos help [QUERY]`**: New command for strategic semantic search over the internal system manual.
- **`vcos config mcp`**: New command to generate JSON configuration blocks for Claude Code and Antigravity.
- **System Manual**: Bootstrapped a library of guides (`claude-code.md`, `nanoclaw.md`, `antigravity.md`) into the user's vault.
- **Improved Init**: `vcos init` now automatically deploys the documentation system.

### Why
To ensure that a clueless user can find answers about integrations (Claude, NanoClaw, Antigravity) without leaving the terminal. This transforms the VCoS from a "package" into a "self-explaining system."

### Files touched
- `src/vcos/cli.py` — Added `help` and `config mcp` commands.
- `src/vcos/data/help/` — [NEW] directory for manual content.
- `AGENTS.md` — Updated with setup instructions for the help system.

## [2026-04-14] — Windows Support & Handover Automation

**Branch**: `main`

### What changed
- Added `scripts/setup-windows.ps1` to automate `uv` and `ffmpeg` installation on Windows via `winget`.
- Updated `AGENTS.md` with a "Platform Detection" logic to guide AI assistants through Windows vs Mac/Linux setup.
- Switched to `uv tool install` for `mempalace` in the official guide for better reliability.
- Verified cross-platform path handling for `vcos status` and `vcos init`.

### Why
To make the system accessible to non-technical founders on Windows. By providing a PowerShell script and platform-specific logic in the agent guide, the AI can now handle the entire environment setup for the user.

### Files touched
- `scripts/setup-windows.ps1` — New automation script.
- `AGENTS.md` — Updated with platform-specific setup instructions.

## [0.1.0] — 2026-04-14

**Branch**: `main`

### Added
- Created the `vcos` Python package structure (`src/vcos`).
- Implemented `vcos init` for vault scaffolding.
- Ported core skills: `archive`, `retrieve`, `compose`, `mom`, `standup`.
- Created `config.py` for environment-driven path resolution (no more hardcoded paths).
- Bundled **Marshall** as the default example advisor.
- Added `AGENTS.md` and `CLAUDE.md` for AI-assisted setup and extensibility.
- Created vault scaffold with directory structure and initial templates (`style.md`, `mom.md`).

### Why
Initial release of the Virtual Chief of Staff as a distributable package. The goal is to make the system modular, portable, and easy for non-technical users to set up using AI tools.
