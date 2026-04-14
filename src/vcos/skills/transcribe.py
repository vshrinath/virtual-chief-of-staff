import click
import os
from pathlib import Path
from vcos.config import get_vault
from vcos.skills.archive import archive as archive_skill

@click.command()
@click.argument("audio_path", type=click.Path(exists=True))
@click.option("--model", default="base", help="Whisper model to use (tiny, base, small, medium, large).")
@click.option("--archive", is_flag=True, help="Automatically archive the transcript to the inbox.")
@click.pass_context
def transcribe(ctx, audio_path, model, archive):
    """Transcribe an audio file locally using Whisper."""
    try:
        import whisper
    except ImportError:
        click.echo("❌ Error: Whisper is not installed.")
        click.echo("Tip: To use this skill, reinstall VCoS with: pip install \"vcos[whisper]\"")
        return

    click.echo(f"🔄 Loading Whisper model '{model}'...")
    whisper_model = whisper.load_model(model)
    
    click.echo(f"🎧 Transcribing {audio_path}...")
    result = whisper_model.transcribe(audio_path)
    text = result["text"].strip()
    
    click.echo("\n--- TRANSCRIPT ---")
    click.echo(text)
    click.echo("------------------\n")

    if archive:
        filename = Path(audio_path).stem + ".md"
        dest_path = f"writing/articles/1-inbox/{filename}"
        click.echo(f"📥 Archiving to {dest_path}...")
        ctx.invoke(archive_skill, content=text, path=dest_path)
    else:
        click.echo("Tip: Use --archive to save this transcript to your vault inbox.")
