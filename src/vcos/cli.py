"""
cli.py — Click-based CLI dispatcher.

Every capability is a skill registered here as a sub-command.
To add a new skill: implement it in skills/<name>.py, then register it below.
"""

import json
import click
from dotenv import load_dotenv

load_dotenv()


@click.group()
@click.version_option()
def main():
    """Virtual Chief of Staff — your personal intelligence system."""
    pass


# ---------------------------------------------------------------------------
# vcos init
# ---------------------------------------------------------------------------

@main.command()
@click.option("--vault", required=True, help="Path where the vault should be created")
def init(vault):
    """Scaffold a new vault and write a .env template."""
    import shutil
    from pathlib import Path

    vault_path = Path(vault).expanduser().resolve()
    scaffold_src = Path(__file__).parent / "data" / "scaffold"

    # Copy scaffold structure
    if vault_path.exists():
        click.echo(f"Vault already exists at {vault_path}. Skipping scaffold.")
    else:
        shutil.copytree(scaffold_src, vault_path)
        click.echo(f"✅ Vault created at {vault_path}")

    # Write .env template
    env_file = vault_path / ".env"
    if env_file.exists():
        click.echo(f".env already exists — not overwriting.")
    else:
        env_file.write_text(
            f"VCOS_VAULT_PATH={vault_path}\n"
            "ANTHROPIC_API_KEY=YOUR_ANTHROPIC_KEY_HERE\n"
            "OPENAI_API_KEY=YOUR_OPENAI_KEY_HERE\n"
            "FATHOM_API_KEY=YOUR_FATHOM_KEY_HERE\n"
            "MEMPALACE_PALACE_PATH=~/.mempalace/palace\n"
        )
        click.echo(f"✅ .env template written to {env_file}")

    # Copy example advisor (Marshall)
    advisors_dir = vault_path / "work-style" / "advisors"
    marshall_src = Path(__file__).parent / "data" / "advisors" / "marshall.md"
    marshall_dst = advisors_dir / "marshall.md"
    if marshall_src.exists() and not marshall_dst.exists():
        shutil.copy(marshall_src, marshall_dst)
        click.echo(f"✅ Example advisor (Marshall) copied to {marshall_dst}")

    # Bootstrap Help Documentation
    help_dir = vault_path / "system" / "docs"
    help_src = Path(__file__).parent / "data" / "help"
    if help_src.exists():
        if help_dir.exists():
            shutil.rmtree(help_dir)
        shutil.copytree(help_src, help_dir)
        click.echo(f"✅ Help manual bootstrapped to {help_dir}")

    click.echo("\nNext steps:")
    click.echo(f"  1. Fill in API keys in {env_file}")
    click.echo("  2. Run: vcos config mcp  (to connect Claude/Antigravity)")
    click.echo("  3. Run: uv tool install mempalace && mempalace init ~/.mempalace/palace")
    click.echo(f"  4. Run: mempalace mine {vault_path} --wing personal")
    click.echo("  5. Run: vcos help 'getting started' to explore the manual")


# ---------------------------------------------------------------------------
# vcos archive
# ---------------------------------------------------------------------------

@main.command()
@click.option("--content", required=True, help="Markdown content to archive")
@click.option("--path", required=True, help="Relative path within vault (e.g. projects/my-project/note.md)")
@click.option("--project", default=None, help="Project tag")
@click.option("--stage", default=None, help="Stage tag")
@click.option("--type", "file_type", default=None, help="Type tag")
@click.option("--theme", default=None, help="Theme tag")
def archive(content, path, project, stage, file_type, theme):
    """Archive content to the vault with front matter and index update."""
    from vcos.skills.archive import archive as _archive
    result = _archive(content, path, project, stage, file_type, theme)
    click.echo(f"Archived to: {result}")


# ---------------------------------------------------------------------------
# vcos retrieve
# ---------------------------------------------------------------------------

@main.command()
@click.argument("query")
@click.option("--project", default=None, help="Filter by project")
@click.option("--stage", default=None, help="Filter by stage (comma-separated)")
@click.option("--type", "file_type", default=None, help="Filter by type (comma-separated)")
@click.option("--limit", default=10, show_default=True, help="Max results")
@click.option("--format", "fmt", default="text", show_default=True,
              type=click.Choice(["json", "text"]), help="Output format")
def retrieve(query, project, stage, file_type, limit, fmt):
    """Semantic search across your vault via MemPalace."""
    from vcos.skills.retrieve import search
    import os

    results = search(query, limit, project, stage, file_type)

    if not results:
        click.echo("No results found.")
        return

    if fmt == "json":
        click.echo(json.dumps(results, indent=2))
    else:
        for res in results:
            source_name = os.path.basename(res["source"]) if res.get("source") else "unknown"
            click.echo(f"\n--- {source_name} (score: {res['score']:.2f}) ---")
            click.echo(res["content"])


# ---------------------------------------------------------------------------
# vcos compose
# ---------------------------------------------------------------------------

@main.command()
@click.option("--query", required=True, help="What to compose or research")
@click.option("--type", "task_type", default="idea",
              type=click.Choice(["proposal", "writing", "idea"]),
              help="Type of task")
@click.option("--mode", default="deep", type=click.Choice(["fast", "deep"]),
              show_default=True, help="Fast or deep context retrieval")
@click.option("--project", default=None, help="Filter context to a project")
@click.option("--stage", default=None, help="Filter context to a stage")
def compose(query, task_type, mode, project, stage):
    """Assemble a context pack for drafting (retrieve + advisor context)."""
    from vcos.skills.compose import compose as _compose
    pack = _compose(query, task_type, mode, project, stage)
    click.echo(json.dumps(pack, indent=2))


# ---------------------------------------------------------------------------
# vcos mom
# ---------------------------------------------------------------------------

@main.command()
@click.argument("command", default="list", required=False)
@click.argument("meeting_num", required=False, type=int)
@click.argument("project_path", required=False, default="general")
def mom(command, meeting_num, project_path):
    """Meeting minutes. List recent meetings or process one from Fathom.

    \b
    Usage:
      vcos mom list
      vcos mom 1 my-project
    """
    from vcos.skills.mom import list_meetings, process_meeting
    if command == "list" or meeting_num is None:
        list_meetings()
    else:
        try:
            num = int(command)
            process_meeting(num, project_path)
        except ValueError:
            click.echo(f"Unknown command: {command}. Use 'list' or a meeting number.")


# ---------------------------------------------------------------------------
# vcos standup
# ---------------------------------------------------------------------------

@main.command()
def standup():
    """Generate your morning briefing from vault activity."""
    from vcos.skills.standup import run
    run()


# ---------------------------------------------------------------------------
# vcos status
# ---------------------------------------------------------------------------

@main.command()
@click.pass_context
def status(ctx):
    """Diagnose the VCoS environment and health."""
    from vcos.skills.status import status as _status
    ctx.invoke(_status)


# ---------------------------------------------------------------------------
# vcos auth
# ---------------------------------------------------------------------------

@main.command()
@click.option("--key-type", type=click.Choice(["anthropic", "openai"]), help="Provider")
def auth(key_type):
    """Guide the user through API key configuration."""
    from vcos.skills.auth import auth as _auth
    import sys
    # Re-triggering Click's context for sub-command
    from click.testing import CliRunner
    # Actually just calling the function is cleaner if we pass the param
    _auth.callback(key_type)


# ---------------------------------------------------------------------------
# vcos transcribe
# ---------------------------------------------------------------------------

@main.command()
@click.argument("audio_path", type=click.Path(exists=True))
@click.option("--model", default="base", help="Whisper model (tiny, base, small, medium, large)")
@click.option("--archive", is_flag=True, help="Auto-archive to inbox")
@click.pass_context
def transcribe(ctx, audio_path, model, archive):
    """Transcribe an audio file locally using Whisper."""
    from vcos.skills.transcribe import transcribe as _transcribe
    ctx.invoke(_transcribe, audio_path=audio_path, model=model, archive=archive)


# ---------------------------------------------------------------------------
# vcos help
# ---------------------------------------------------------------------------

@main.command()
@click.argument("query", required=False)
def help(query):
    """Search the VCoS manual for integration and usage guides."""
    if not query:
        click.echo("Usage: vcos help <query>")
        click.echo("Examples: 'vcos help claude', 'vcos help nanoclaw'")
        return

    from vcos.skills.retrieve import search
    import os
    
    # We search specifically in the 'system' project where help docs are tagged
    # Note: 'system' tag should be added during mempalace mine
    results = search(query, limit=3, project="system")

    if not results:
        click.echo("No help found for that query. Try 'vcos help overview'.")
        return

    for res in results:
        source_name = os.path.basename(res["source"]) if res.get("source") else "manual"
        click.echo(f"\n📚 --- Manual: {source_name} ---")
        click.echo(res["content"])


# ---------------------------------------------------------------------------
# vcos config
# ---------------------------------------------------------------------------

@main.group()
def config():
    """Configuration helpers."""
    pass


@config.command()
@click.option("--agent", type=click.Choice(["claude", "antigravity"]), default="claude")
def mcp(agent):
    """Generate the JSON config for MCP agents (Claude Code, Antigravity)."""
    from vcos.config import get_palace_path
    import json
    
    try:
        palace = get_palace_path()
    except RuntimeError:
        palace = "/path/to/your/vcos/palace"

    config_obj = {
        "vcos-memory": {
            "command": "uvx",
            "args": ["mempalace-mcp"],
            "env": {
                "MEMPALACE_PALACE_PATH": str(palace)
            }
        }
    }
    
    click.echo(f"\nCopy this block into your mcp_config.json for {agent}:\n")
    click.echo(json.dumps(config_obj, indent=2))
    click.echo("\nLocation of mcp_config.json:")
    click.echo("- Mac: ~/Library/Application Support/Claude/mcp_config.json")
    click.echo("- Windows: %APPDATA%\\Claude\\mcp_config.json")
