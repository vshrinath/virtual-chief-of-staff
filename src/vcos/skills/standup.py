import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from vcos.config import get_vault

def load_state(vault_root: Path):
    # In the new structure, we'll look for state in the vault's data directory
    state_file = vault_root / "data" / "nb_sync_state.json"
    if not state_file.exists():
        return None
    with open(state_file, 'r', encoding="utf-8") as f:
        return json.load(f)

def get_recent_activity(vault_root: Path, state, hours=24):
    """Filter activity from the last X hours."""
    now = datetime.now()
    since = now - timedelta(hours=hours)
    
    recent_files = []
    
    # The state file tracks seen files. If it doesn't exist, we fallback to a disk walk.
    if state and "files" in state:
        for rel_path_str in state.get("files", {}):
            abs_path = vault_root / rel_path_str
            if abs_path.exists():
                mtime = datetime.fromtimestamp(abs_path.stat().st_mtime)
                if mtime > since:
                    recent_files.append({
                        "path": rel_path_str,
                        "mtime": mtime,
                        "type": "youtube" if "yt/" in rel_path_str else "project"
                    })
    else:
        # Fallback: scan projects and writing directories
        scan_dirs = ["projects", "writing"]
        for d in scan_dirs:
            path = vault_root / d
            if path.exists():
                for root, _, files in os.walk(path):
                    for f in files:
                        if f.startswith("."): continue
                        abs_f = Path(root) / f
                        mtime = datetime.fromtimestamp(abs_f.stat().st_mtime)
                        if mtime > since:
                            recent_files.append({
                                "path": str(abs_f.relative_to(vault_root)),
                                "mtime": mtime,
                                "type": "project"
                            })

    return recent_files

def format_briefing(recent_files):
    if not recent_files:
        return "☕ No major brain activity in the last 24 hours. A good day for deep work!"

    projects = {}
    videos = []

    for item in recent_files:
        path_obj = Path(item["path"])
        if item["type"] == "project":
            parts = path_obj.parts
            # Extract project name: projects/<name>/...
            if len(parts) >= 2 and parts[0] == "projects":
                p_name = parts[1]
                if p_name not in projects:
                    projects[p_name] = []
                projects[p_name].append(path_obj.name)
            else:
                # Fallback for writing or other structures
                p_name = parts[0]
                if p_name not in projects:
                    projects[p_name] = []
                projects[p_name].append(path_obj.name)
        else:
            videos.append(path_obj.name)

    output = ["🌅 *Morning Standup*"]
    output.append(f"_{datetime.now().strftime('%A, %b %d')}_")
    output.append("\n---")

    if projects:
        output.append("\n📂 *Activity Intelligence*")
        for p_name, files in projects.items():
            output.append(f"• *{p_name.upper()}*: {len(files)} updates")

    if videos:
        output.append("\n📺 *Video Vault*")
        for v in videos[:3]:
            output.append(f"• {v}")
        if len(videos) > 3:
            output.append(f"• ...and {len(videos)-3} more.")

    output.append("\n---")
    output.append("💡 *Strategic Prompt*: \"How do yesterday's updates change our priority for today?\"")
    
    return "\n".join(output)

def run():
    vault_root = get_vault()
    state = load_state(vault_root)
    
    recent = get_recent_activity(vault_root, state)
    briefing = format_briefing(recent)
    
    print(briefing)
