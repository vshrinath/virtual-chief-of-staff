import os
import sys
import json
import re
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from vcos.config import get_vault, get_mempalace_bin, get_palace_path

# Fathom API
FATHOM_BASE_URL = "https://api.fathom.ai/external/v1"

def get_fathom_key():
    key = os.environ.get("FATHOM_API_KEY")
    if not key:
        print("⚠️  FATHOM_API_KEY not set in environment")
    return key

def get_meetings(limit=10):
    """Get recent meetings from Fathom"""
    key = get_fathom_key()
    if not key:
        return []
    try:
        response = requests.get(
            f"{FATHOM_BASE_URL}/meetings",
            headers={"X-Api-Key": key},
            params={"limit": limit},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"❌ Error fetching meetings: {e}")
        return []

def get_transcript(recording_id):
    """Get transcript for a meeting"""
    key = get_fathom_key()
    if not key:
        return None
    try:
        response = requests.get(
            f"{FATHOM_BASE_URL}/recordings/{recording_id}/transcript",
            headers={"X-Api-Key": key},
            timeout=30
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        return None

def parse_transcript(transcript_json):
    """Parse JSON transcript to formatted text"""
    try:
        data = json.loads(transcript_json)
        lines = []
        for item in data.get("transcript", []):
            speaker = item.get("speaker", {}).get("display_name", "Unknown")
            text = item.get("text", "").strip()
            if text:
                lines.append(f"{speaker}: {text}")
        return "\n".join(lines)
    except:
        return transcript_json[:3000]

def list_meetings():
    """List recent meetings"""
    meetings = get_meetings(limit=10)
    if not meetings:
        print("❌ No meetings found or Fathom API key not configured")
        return

    print(f"\n📅 Recent Meetings (1-{len(meetings)}):")
    print("=" * 60)
    for i, m in enumerate(meetings, 1):
        title = m.get("title", "Untitled")
        date_str = "Unknown"
        if m.get("created_at"):
            try:
                dt = datetime.fromisoformat(m["created_at"].replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        print(f"  {i}. {title}")
        print(f"     Date: {date_str}")
        print()

def process_meeting(meeting_num, project_path="general"):
    """Process meeting and generate minutes"""
    vault_root = get_vault()
    projects_dir = vault_root / "projects"
    
    meetings = get_meetings(limit=10)
    if not meetings:
        print("❌ No meetings available")
        return False

    if meeting_num < 1 or meeting_num > len(meetings):
        print(f"❌ Invalid meeting number. Choose 1-{len(meetings)}")
        return False

    meeting = meetings[meeting_num - 1]

    # Extract metadata
    date_str = "Unknown"
    if meeting.get("created_at"):
        try:
            dt = datetime.fromisoformat(meeting["created_at"].replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
        except:
            pass

    title = meeting.get("title", "Untitled Meeting")
    participants = [inv.get("name", "") for inv in meeting.get("calendar_invitees", []) if inv.get("name")]

    print(f"\n📝 Processing: {title}")
    print(f"📅 Date: {date_str}")
    print(f"👥 Participants: {len(participants)}")

    # Get transcript
    recording_id = meeting.get("recording_id")
    if not recording_id:
        print("❌ No recording ID found")
        return False

    print("⏳ Fetching transcript...")
    transcript_json = get_transcript(recording_id)
    if not transcript_json:
        print("❌ Could not fetch transcript")
        return False

    transcript_text = parse_transcript(transcript_json)
    print(f"✅ Transcript: {len(transcript_text.split(chr(10)))} lines")

    # Save transcript
    project_dir = projects_dir / project_path
    meetings_dir = project_dir / "meetings"
    meetings_dir.mkdir(parents=True, exist_ok=True)

    title_slug = re.sub(r'[^\w\s-]', '', title).lower()
    title_slug = re.sub(r'[-\s]+', '-', title_slug).strip('-')[:50]

    transcript_file = meetings_dir / f"{date_str}-{title_slug}-transcript.txt"
    with open(transcript_file, 'w', encoding="utf-8") as f:
        f.write(f"Meeting: {title}\n")
        f.write(f"Date: {date_str}\n")
        f.write(f"Participants: {', '.join(participants)}\n")
        f.write("=" * 60 + "\n\n")
        f.write(transcript_text)

    print(f"✅ Saved: {transcript_file.relative_to(vault_root)}")

    # Re-index this client folder in mempalace
    try:
        mp_bin = get_mempalace_bin()
        palace_path = get_palace_path()
        print(f"⏳ Updating memory index for {project_path}...")
        
        # Room name logic: project name used as room
        room = project_path.replace("-", "_")
        
        env = os.environ.copy()
        env["MEMPALACE_PALACE_PATH"] = str(palace_path)
        
        result = subprocess.run(
            [mp_bin, "mine", str(project_dir), "--wing", "consulting", "--room", room],
            env=env, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ Memory index updated")
        else:
            print(f"⚠️  Index update failed (non-critical): {result.stderr.strip()}")
    except Exception:
        pass

    print(f"\n💡 Next: Use your LLM to summarize based on: {transcript_file}")
    return True
