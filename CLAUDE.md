# CLAUDE.md

You are helping the user set up or extend their Virtual Chief of Staff system.

Read AGENTS.md first for the full setup procedure.

## Quick Reference

- Vault path: `$VCOS_VAULT_PATH` (set in .env)
- MemPalace palace: `$MEMPALACE_PALACE_PATH` (default: `~/.mempalace/palace`)
- CLI entry: `vcos --help`
- Skills live in: `src/vcos/skills/`
- Advisors live in: `$VCOS_VAULT_PATH/work-style/advisors/`

## Adding a New Skill

1. Create `src/vcos/skills/<skill_name>.py`
2. Implement a `main()` function
3. Register it as a Click command in `src/vcos/cli.py`
4. Re-install: `uv tool install .`

## Coding Conventions

- All path resolution goes through `from vcos.config import get_vault`
- Never hardcode paths
- Fail loud: raise `RuntimeError` with an actionable message if config is missing
- Match the pattern in existing skills for consistency
