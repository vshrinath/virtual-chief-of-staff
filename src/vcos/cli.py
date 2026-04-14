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

    click.echo("\nNext steps:")
    click.echo(f"  1. Fill in API keys in {env_file}")
    click.echo("  2. Run: pip install mempalace && mempalace init ~/.mempalace/palace")
    click.echo(f"  3. Run: mempalace mine {vault_path} --wing personal")
    click.echo("  4. Run: vcos retrieve 'test' to verify")


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
