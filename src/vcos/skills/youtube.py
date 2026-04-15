import click
import re
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from vcos.config import get_vault

# Try to import yt-dlp
try:
    import yt_dlp
    HAS_YT_DLP = True
except ImportError:
    HAS_YT_DLP = False

def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]+)',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_info(url):
    if not HAS_YT_DLP:
        return None, None

    try:
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            metadata = {
                'title': info.get('title', 'Untitled'),
                'duration': info.get('duration', 0),
                'upload_date': info.get('upload_date', ''),
                'url': url,
                'channel': info.get('uploader', ''),
            }

            subtitles = info.get('subtitles', {}) or info.get('automatic_captions', {})
            transcript_text = None

            if 'en' in subtitles:
                sub_url = subtitles['en'][0]['url']
                import urllib.request
                with urllib.request.urlopen(sub_url) as response:
                    transcript_text = response.read().decode('utf-8')

            return metadata, transcript_text

    except Exception as e:
        click.echo(f"❌ Error fetching video: {e}")
        return None, None

def format_duration(seconds):
    if seconds < 3600:
        return f"{seconds // 60:02d}:{seconds % 60:02d}"
    else:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

@click.command()
@click.argument("url", required=False)
@click.option("--save-dir", help="Subdirectory in vault to save to (e.g., 'yt').")
@click.option("--cleanup", help="Delete the raw/ folder in the specified directory.")
def youtube(url, save_dir, cleanup):
    """Fetch YouTube transcripts and metadata with a clean workflow."""
    if cleanup:
        vault = get_vault() / cleanup
        raw_dir = vault / "raw"
        if raw_dir.exists():
            shutil.rmtree(raw_dir)
            click.echo(f"🗑️  Cleaned up raw/ in {cleanup}")
        else:
            click.echo(f"ℹ️  No raw/ folder found in {cleanup}")
        return

    if not url:
        click.echo("❌ Error: Missing YouTube URL or --cleanup [dir]")
        return

    if not HAS_YT_DLP:
        click.echo("❌ Error: yt-dlp is not installed.")
        click.echo("Tip: Reinstall VCoS with: pip install \"vcos[youtube]\"")
        return

    video_id = extract_video_id(url)
    if not video_id:
        click.echo("❌ Error: Invalid YouTube URL")
        return

    click.echo(f"📺 Processing video: {video_id}")
    click.echo("⏳ Fetching metadata and transcript...")

    metadata, transcript = get_video_info(url)
    if not metadata:
        return

    title = metadata['title']
    duration_str = format_duration(metadata['duration'])

    click.echo(f"\n✅ Title: {title}")
    click.echo(f"⏱️  Duration: {duration_str}")
    click.echo(f"👤 Channel: {metadata['channel']}")

    # Setup directories in vault
    vault = get_vault()
    output_dir = vault / (save_dir or "youtube")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    title_slug = re.sub(r'[^\w\s-]', '', title).lower()
    title_slug = re.sub(r'[-\s]+', '-', title_slug).strip('-')[:50]

    # Save transcript to raw/
    transcript_file = raw_dir / f"{date_str}-{title_slug}-transcript.txt"
    if transcript:
        with open(transcript_file, 'w') as f:
            f.write(f"Title: {title}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Duration: {duration_str}\n")
            f.write(f"Channel: {metadata['channel']}\n")
            f.write("=" * 60 + "\n\n")
            f.write(transcript)
        click.echo(f"✅ Transcript saved to raw/: {transcript_file.name}")
    else:
        click.echo("⚠️  No transcript available")

    # Save metadata to raw/
    metadata_file = raw_dir / f"{date_str}-{title_slug}-metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    click.echo(f"\n📄 Saved intermediates to {output_dir.relative_to(vault)}/raw/")
    click.echo(f"💡 Next: Ask your agent to process the transcript in raw/ and generate the final .md")
    click.echo(f"🗑️  Then run: vcos youtube --cleanup {save_dir or 'youtube'}")
