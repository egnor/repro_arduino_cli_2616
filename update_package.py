#!/usr/bin/env python3

import json
import hashlib
from pathlib import Path
import re
import subprocess
import urllib
import zipfile

repo_dir = Path(__file__).parent
core_name = "egnor_repro2616"
index_path = repo_dir / f"package_{core_name}_index.json"
git_show = subprocess.check_output(
    ["git", "show", f"HEAD:{index_path.name}"],
    text=True, cwd=index_path.parent
)

head_index = json.loads(git_show)
tree_index = json.loads(index_path.read_text())

head_platform = head_index["packages"][0]["platforms"][0]
tree_platform = tree_index["packages"][0]["platforms"][0]

head_version = head_platform["version"]
tree_version = tree_platform["version"]

for old_version in set((head_version, tree_version)):
    old_path = repo_dir / f"{core_name}-{old_version}.zip"
    old_path.unlink(missing_ok=True)

next_version = re.sub(r"\d+$", lambda m: str(int(m.group()) + 1), head_version)
new_path = repo_dir / f"{core_name}-{next_version}.zip"

# make zip file with all files from esp/
with zipfile.ZipFile(new_path, "w") as zf:
    for file in repo_dir.glob("esp/**/*"):
        zf.write(file, file.relative_to(repo_dir))

tree_platform["version"] = next_version
tree_platform["url"] = tree_platform["url"].replace(tree_version, next_version)
tree_platform["archiveFileName"] = new_path.name

zip_bytes = new_path.read_bytes()
tree_platform["size"] = len(zip_bytes)
tree_platform["checksum"] = "SHA-256:" + hashlib.sha256(zip_bytes).hexdigest()

index_path.write_text(json.dumps(tree_index, indent=2) + "\n")
