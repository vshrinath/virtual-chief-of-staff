import click
import os
import shutil
from pathlib import Path
from vcos.config import get_vault, get_palace_path

@click.command()
@click.pass_context
def status(ctx):
    """Diagnose the VCoS environment and health."""
    click.echo("🔍 Diagnosing Virtual Chief of Staff Environment...\n")
    
    # 1. Check Vault
    try:
        vault_path = get_vault()
        click.echo(f"✅ Vault found: {vault_path}")
    except RuntimeError as e:
        click.echo(f"❌ Vault Error: {e}")
        click.echo("   Tip: Set VCOS_VAULT_PATH in your environment or .env file.")
        return

    # 2. Check Directories
    dirs = ["writing/articles/1-inbox", "work-style/advisors", "projects"]
    all_dirs_ok = True
    for d in dirs:
        p = Path(vault_path) / d
        if p.exists():
            click.echo(f"✅ Folder found: {d}")
        else:
            click.echo(f"⚠️ Missing folder: {d} (Run 'vcos init' to fix)")
            all_dirs_ok = False

    # 3. Check MemPalace
    mempalace_cli = shutil.which("mempalace")
    if mempalace_cli:
        click.echo(f"✅ MemPalace CLI found: {mempalace_cli}")
    else:
        click.echo("⚠️ MemPalace CLI not found on PATH.")
        click.echo("   Tip: Run 'pip install mempalace' to enable semantic memory indexing.")

    # 4. Check Palace Database
    palace_path = get_palace_path()
    if os.path.exists(palace_path):
        click.echo(f"✅ Palace Index found: {palace_path}")
    else:
        click.echo(f"⚠️ Palace Index missing at {palace_path}")
        click.echo("   Tip: Run 'mempalace init' to create your memory database.")

    # 5. Check API Keys
    keys = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
    found_keys = [k for k in keys if os.getenv(k)]
    if found_keys:
        click.echo(f"✅ API Keys found: {', '.join(found_keys)}")
    else:
        click.echo("❌ No API Keys found!")
        click.echo("   Tip: Run 'vcos auth' to configure your keys.")

    # 6. Check Whisper (Optional)
    try:
        import whisper
        click.echo("✅ local Transcription (Whisper) is ENABLED.")
    except ImportError:
        click.echo("ℹ️ local Transcription (Whisper) is DISABLED (Lean Version).")
        click.echo("   Tip: To enable, reinstall with 'pip install \"vcos[whisper]\"'.")

    click.echo("\n✨ Diagnosis complete.")
