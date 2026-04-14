import os
from pathlib import Path
from vcos.skills.retrieve import search
from vcos.config import get_vault

def get_style_content() -> str:
    vault_root = get_vault()
    # Look for several possible names for the style file
    possible_names = ["style.md", "How I Write.md", "Writing Style.md", "personal.md"]
    style_dir = vault_root / "work-style"
    
    if style_dir.exists():
        for name in possible_names:
            path = style_dir / name
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
    return ""

def get_advisor_content(name: str) -> str:
    vault_root = get_vault()
    path = vault_root / "work-style" / "advisors" / f"{name.lower()}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def compose(query: str, task_type: str, mode: str = "deep", project: str = None, stage: str = None):
    # 1. Retrieve Context
    # We use the search function directly from the retrieve skill
    limit = 10 if mode == "fast" else 20
    context_data = search(query, project=project, stage=stage, limit=limit)
    
    context_block = ""
    for res in context_data:
        source_basename = os.path.basename(res["source"])
        context_block += f"--- SOURCE: {source_basename} ---\n{res['content']}\n\n"

    # 2. Determine Advisors based on Task Type
    advisors = []
    if task_type == "proposal":
        # Example logic: in a real system, these would be configurable
        advisors = ["marshall"] 
    elif task_type == "writing":
        advisors = ["marshall"]
    else:
        advisors = ["marshall"] # Marshall is our bundled default

    # 3. Assemble Pack
    # This pack is intended to be passed to an LLM (like me, or a standalone LLM call)
    pack = {
        "query": query,
        "context": context_block,
        "style": get_style_content(),
        "advisors": {name: get_advisor_content(name) for name in advisors},
        "mode": mode,
        "task_type": task_type
    }
    
    return pack
