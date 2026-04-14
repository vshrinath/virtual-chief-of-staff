import os
import yaml
import subprocess
import datetime
from pathlib import Path
from vcos.config import get_vault, get_mempalace_bin, get_palace_path

def archive(content: str, path_rel: str, project=None, stage=None, file_type=None, theme=None):
    vault_root = get_vault()
    
    # Resolve Path
    if path_rel.startswith("/"):
        path_rel = path_rel[1:]
    
    file_path = vault_root / path_rel
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Prepare Frontmatter
    frontmatter = {
        "project": project,
        "stage": stage,
        "type": file_type,
        "theme": theme,
        "date_created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Remove None values
    frontmatter = {k: v for k, v in frontmatter.items() if v is not None}

    # Inject Frontmatter
    fm_str = yaml.dump(frontmatter, default_flow_style=False)
    final_content = f"---\n{fm_str}---\n\n{content}"

    # Write File
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    # Trigger incremental mine if mempalace is available
    try:
        mp_bin = get_mempalace_bin()
        palace_path = get_palace_path()
        mine_dir = file_path.parent
        
        env = os.environ.copy()
        env["MEMPALACE_PALACE_PATH"] = str(palace_path)
        
        # We'll rely on the user having a logs dir in their vault or we use a temp log
        log_dir = vault_root / "logs"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / "archivist-rebuild.log"
        
        subprocess.Popen(
            [mp_bin, "mine", str(mine_dir)],
            stdout=open(log_path, "a"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=env
        )
    except Exception:
        # Silently fail if mempalace is not configured, matching original behavior but less chatty
        pass

    return str(file_path)
