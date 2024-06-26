#!/usr/bin/env python3

import json
import hashlib
from pathlib import Path
import re
import subprocess
import urllib
import yaml
import zipfile

repo_dir = Path(__file__).parent
core_name = "egnor_repro2616"
index_path = repo_dir / f"package_{core_name}_index.json"
git_show = subprocess.check_output(
    ["git", "show", f"HEAD:{index_path.name}"],
    text=True, cwd=index_path.parent
)

git_index = json.loads(git_show)
git_platform = git_index["packages"][0]["platforms"][0]
git_version = git_platform["version"]
version = re.sub(r"\d+$", lambda m: str(int(m.group()) + 1), git_version)

index = json.loads(index_path.read_text())
platform = index["packages"][0]["platforms"][0]
zip_path = repo_dir / f"{core_name}-{version}.zip"
old_url = urllib.parse.urlparse(platform["url"])
url_path = re.sub(r"/[^/]*$", f"/{zip_path.name}", old_url.path)
url = old_url._replace(path=url_path)

project_path = repo_dir / "test_sketch" / "sketch.yaml"
project = yaml.load(project_path.read_text(), Loader=yaml.Loader)
project_profile = project["default_profile"]
for project_platform in project["profiles"][project_profile]["platforms"]:
    index_url = urllib.parse.urlparse(project_platform["platform_index_url"])
    if index_url.path.endswith(f"/{index_path.name}"):
        platform_ref = project_platform["platform"]
        platform_ref = re.sub(r"\(\d+(\.\d+)+\)", f"({version})", platform_ref)
        project_platform["platform"] = platform_ref

old_version = platform["version"]
for old_version in set((git_version, old_version)):
    old_zip_path = repo_dir / f"{core_name}-{old_version}.zip"
    old_zip_path.unlink(missing_ok=True)

with zipfile.ZipFile(zip_path, "w") as zf:
    for file in repo_dir.glob("esp32/**/*"):
        zf.write(file, file.relative_to(repo_dir))

zip_bytes = zip_path.read_bytes()

platform["version"] = version
platform["url"] = url.geturl()
platform["archiveFileName"] = zip_path.name
platform["size"] = len(zip_bytes)
platform["checksum"] = "SHA-256:" + hashlib.sha256(zip_bytes).hexdigest()

project_path.write_text(yaml.dump(project))
index_path.write_text(json.dumps(index, indent=2) + "\n")
