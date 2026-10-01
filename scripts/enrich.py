#!/usr/bin/env python3
"""Copy star counts from approved snapshot data; no resource API calls."""

import json
import pathlib
import re
from urllib.parse import urlsplit


def repository_key(url):
    parsed = urlsplit(url)
    parts = parsed.path.strip("/").split("/")
    return (
        "/".join(parts[:2]).casefold()
        if parsed.hostname == "github.com" and len(parts) >= 2
        else None
    )


def star_counts(snapshots):
    counts = {}

    def remember(repo, stars):
        if isinstance(repo, str) and isinstance(stars, int) and stars >= 0:
            key = repo.removeprefix("https://github.com/").strip("/").casefold()
            if len(key.split("/")) == 2:
                counts[key] = max(counts.get(key, 0), stars)

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            repo = (
                node.get("repo") or node.get("full_name") or node.get("repo_url") or node.get("url")
            )
            stars = node.get("stars")
            if isinstance(repo, str) and repo.startswith("https://github.com/"):
                repo = repository_key(repo)
            if stars is None and isinstance(node.get("sourceMeta"), dict):
                stars = node["sourceMeta"].get("stars")
                repo = node["sourceMeta"].get("repo") or repo
            if stars is None and isinstance(node.get("metrics"), dict):
                stars = node["metrics"].get("stars")
            remember(repo, stars)
            if isinstance(node.get("repos"), dict):
                for repo, meta in node["repos"].items():
                    remember(repo, meta.get("stars"))
            for value in node.values():
                walk(value)

    import yaml

    for folder in snapshots.iterdir():
        if not folder.is_dir():
            continue
        for prefix in ["data", "catalog", "docs/data"]:
            base = folder / prefix
            if not base.exists():
                continue
            for file in base.rglob("*"):
                if file.suffix not in (".json", ".yaml", ".yml") or "/stars/" in str(file):
                    continue
                value = (
                    json.loads(file.read_text())
                    if file.suffix == ".json"
                    else yaml.safe_load(file.read_text())
                )
                walk(value)
    # README-only lists publish rounded star counts. Use those solely where no
    # exact numeric snapshot exists. They are explicitly marked approximate.
    approximate = {}
    for file in snapshots.rglob("*.md"):
        if file.name.lower() != "readme.md":
            continue
        for line in file.read_text().splitlines():
            match = re.search(r"(?:⭐|★)\s*([\d,.]+)\s*([kKmM]?)", line)
            repos = re.findall(r"https://github\.com/([\w.-]+/[\w.-]+)", line)
            if match and len(set(repos)) == 1:
                number = float(match[1].replace(",", "")) * (
                    1000 if match[2].lower() == "k" else 1000000 if match[2].lower() == "m" else 1
                )
                approximate[repos[0].casefold()] = round(number)
    return counts, approximate


if __name__ == "__main__":
    import sys

    data = json.loads(pathlib.Path(sys.argv[1]).read_text())
    exact, approx = star_counts(pathlib.Path(sys.argv[2]))
    for entry in data["entries"]:
        repo = repository_key(entry["url"])
        entry["stars"] = exact.get(repo, approx.get(repo))
        entry["starsApproximate"] = repo not in exact and repo in approx
        entry["starsAsOf"] = data["collectedAt"] if entry["stars"] is not None else None
        entry["starsRepository"] = repo if entry["stars"] is not None else None
    pathlib.Path(sys.argv[1]).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(
        "Entries with available repository stars:",
        sum(e["stars"] is not None for e in data["entries"]),
    )
