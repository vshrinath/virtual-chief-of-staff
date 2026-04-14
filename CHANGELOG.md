# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
