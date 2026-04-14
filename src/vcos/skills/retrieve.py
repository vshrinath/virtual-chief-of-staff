import os
import json
import subprocess
import re
import yaml
from pathlib import Path
from vcos.config import get_vault, get_mempalace_bin, get_palace_path

def resolve_path(source_ref: str) -> Path | None:
    """
    Converts MemPalace source ref (wing/room/filename) to absolute file path.
    """
    vault_root = get_vault()
    parts = source_ref.split("/")
    if len(parts) < 2:
        return None
    
    wing = parts[0]
    room = parts[1]
    filename = "/".join(parts[2:])

    # Ported logic from original retriever.py, adapted for get_vault()
    if wing == "consulting":
        return vault_root / "projects" / room / filename
    elif wing == "library":
        possible_paths = [
            vault_root / "yt" / filename,
            vault_root / "references" / "kindle" / filename,
            vault_root / "references" / "Clippings" / filename,
            vault_root / room / filename
        ]
        for p in possible_paths:
            if p.exists():
                return p
        return possible_paths[-1]
    elif wing == "writing":
        writing_root = vault_root / "writing"
        if writing_root.exists():
            for root, dirs, files in os.walk(writing_root):
                if filename and filename in files:
                    return Path(root) / filename
                if room in files:
                    return Path(root) / room
        return vault_root / "writing" / room / filename

    # Default fallback: try to find it relative to vault root directly
    fallback = vault_root / source_ref
    if fallback.exists():
        return fallback

    return None

def infer_metadata(file_path: Path):
    """
    Infers project, stage, and type from path and frontmatter.
    """
    meta = {
        "project": "general",
        "stage": "discovery",
        "type": "note"
    }

    if not file_path or not file_path.exists():
        return meta

    # 1. Infer from Path
    path_low = str(file_path).lower()
    
    # Project
    match = re.search(r"/projects/([^/]+)/", path_low)
    if match:
        meta["project"] = match.group(1)
    
    # Stage
    stages = ["discovery", "proposal", "delivery", "raw", "draft", "published", "0-raw", "4-published"]
    for s in stages:
        if f"/{s}/" in path_low:
            meta["stage"] = s
            break
    
    # Type
    types = ["proposal", "case-study", "transcript", "writing", "idea", "article", "post"]
    for t in types:
        if t in path_low or t in file_path.name.lower():
            meta["type"] = t
            break

    # 2. Extract from Frontmatter
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                fm_data = yaml.safe_load(fm_match.group(1))
                if isinstance(fm_data, dict):
                    for k in meta:
                        if k in fm_data:
                            meta[k] = fm_data[k]
    except Exception:
        pass

    return meta

def search(query, limit=20, project=None, stage=None, file_type=None):
    mp_bin = get_mempalace_bin()
    palace_path = get_palace_path()

    # Set Env
    env = os.environ.copy()
    env["MEMPALACE_PALACE_PATH"] = str(palace_path)

    # Fetch more to allow for filtering
    results_to_fetch = limit * 3
    cmd = [mp_bin, "--palace", str(palace_path), "search", query, "--results", str(results_to_fetch)]
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        raw_output = result.stdout
    except subprocess.CalledProcessError:
        return []

    # Parse Output
    result_blocks = re.split(r'\n(?=\s+\[\d+\])', raw_output)
    parsed_results = []
    
    for block in result_blocks:
        if not block.strip() or "[Results for:" in block:
            continue
        
        # Extract Wing/Room
        wr_match = re.search(r'\[\d+\]\s+([^\s/]+)\s*/\s*([^\s\n]+)', block)
        if not wr_match:
            continue
        wing = wr_match.group(1).strip()
        room = wr_match.group(2).strip()

        # Extract Source
        source_match = re.search(r'Source:\s*([^\n]+)', block)
        if not source_match:
            continue
        filename = source_match.group(1).strip()
        
        # Extract Match (Score)
        match_score_match = re.search(r'Match:\s*([\d.]+)', block)
        score = float(match_score_match.group(1)) if match_score_match else 0.0
        
        # Extract Content
        content_parts = re.split(r'Match:\s*[\d.]+', block)
        content = content_parts[-1].strip() if len(content_parts) > 1 else ""
        
        source_ref = f"{wing}/{room}/{filename}"
        file_path = resolve_path(source_ref)
        if not file_path:
            continue
            
        metadata = infer_metadata(file_path)
        
        # Filtering
        if project and metadata["project"] != project:
            continue
        if stage:
            stages_list = [s.strip() for s in stage.split(",")]
            if metadata["stage"] not in stages_list:
                continue
        if file_type:
            types_list = [t.strip() for t in file_type.split(",")]
            if metadata["type"] not in types_list:
                continue
        
        # Ranking Boost
        final_score = score
        if project and metadata["project"] == project:
            final_score += 0.2
        if stage and metadata["stage"] in (stage.split(",") if stage else []):
            final_score += 0.1
        
        parsed_results.append({
            "content": content,
            "source": str(file_path),
            "metadata": metadata,
            "score": final_score
        })

    # Deduplication
    unique_results = []
    seen_contents = set()
    for res in parsed_results:
        norm_content = re.sub(r"\s+", " ", res["content"]).strip()[:300] 
        if norm_content not in seen_contents:
            unique_results.append(res)
            seen_contents.add(norm_content)
    
    unique_results.sort(key=lambda x: x["score"], reverse=True)
    return unique_results[:limit]
