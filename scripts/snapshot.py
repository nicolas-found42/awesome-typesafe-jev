#!/usr/bin/env python3
"""Download only the twelve approved repositories, pinned to a commit each."""

import concurrent.futures
import io
import json
import pathlib
import subprocess
import sys
import tarfile
import urllib.request

from collect import REPOS

root = pathlib.Path(sys.argv[1])
root.mkdir(parents=True, exist_ok=True)


def fetch(repo):
    meta = json.loads(subprocess.check_output(["gh", "api", "repos/" + repo]))
    sha = json.loads(
        subprocess.check_output(
            ["gh", "api", "repos/" + repo + "/commits/" + meta["default_branch"]]
        )
    )["sha"]
    folder = root / repo.replace("/", "__")
    folder.mkdir(exist_ok=True)
    with urllib.request.urlopen(
        "https://codeload.github.com/" + repo + "/tar.gz/" + sha
    ) as response:
        archive = tarfile.open(fileobj=io.BytesIO(response.read()), mode="r:gz")
    files = []
    for member in archive.getmembers():
        if not member.isfile():
            continue
        relative = pathlib.PurePosixPath(*pathlib.PurePosixPath(member.name).parts[1:])
        if ".." in relative.parts or relative.is_absolute():
            raise ValueError("Unsafe archive member")
        destination = folder / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        extracted = archive.extractfile(member)
        if extracted is None:
            raise ValueError("Archive file could not be read")
        destination.write_bytes(extracted.read())
        files.append({"path": str(relative), "size": member.size})
    record = {
        "repo": repo,
        "url": "https://github.com/" + repo,
        "sha": sha,
        "branch": meta["default_branch"],
        "files": files,
    }
    (folder / "_snapshot.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    records = list(pool.map(fetch, REPOS))
(root / "manifest.json").write_text(json.dumps(records, indent=2) + "\n")
print(f"Downloaded {len(records)} pinned source repositories to {root}")
