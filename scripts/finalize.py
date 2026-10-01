#!/usr/bin/env python3
"""Publish standalone catalog fields; keep extraction provenance in a local audit."""

import json
import pathlib
from collections import Counter
from urllib.parse import urlsplit

from taxonomy import all_subcategories

ROOT = pathlib.Path(__file__).resolve().parents[1]


def finalize():
    data = json.loads((ROOT / "data/entries.json").read_text())
    if data["schemaVersion"] == 2:
        data = json.loads((ROOT / ".local/catalog-audit.json").read_text())
    groups = json.loads((ROOT / ".local/subcategory-groups.json").read_text())
    assignment = {}
    judgments = []
    for file in sorted((ROOT / ".local/subcategory-batches").glob("*.result.json")):
        batch = json.loads(file.with_name(file.name.replace(".result.json", ".json")).read_text())
        result = json.loads(file.read_text())
        if len(result.get("results", [])) != len(batch["items"]):
            raise ValueError(f"Incomplete classification batch: {file}")
        for record in result["results"]:
            subcategory = (
                record["classification"]
                if record["decision"] == "auto"
                else batch["parent"] + "-general"
            )
            for identity in groups[record["id"]]:
                assignment[identity] = subcategory
            judgments.append({"group": record["id"], "assigned": subcategory, "judgment": record})
    if len(assignment) != len(data["entries"]):
        raise ValueError("Not every resource has a subcategory")
    full_audit = {**data, "subcategoryJudgments": judgments}
    (ROOT / ".local/catalog-audit.json").write_text(
        json.dumps(full_audit, ensure_ascii=False, indent=2) + "\n"
    )
    for entry in data["entries"]:
        assigned = assignment[entry["id"]]
        if assigned.endswith("-general"):
            host = (urlsplit(entry["url"]).hostname or "").removeprefix("www.")
            kind = (
                "projects"
                if host in ("github.com", "gitlab.com", "codeberg.org")
                else "posts"
                if host
                in (
                    "x.com",
                    "twitter.com",
                    "reddit.com",
                    "news.ycombinator.com",
                    "bsky.app",
                    "threads.net",
                )
                else "videos"
                if host in ("youtube.com", "youtu.be", "vimeo.com")
                else "packages"
                if host in ("npmjs.com", "pypi.org", "crates.io", "pkg.go.dev", "nuget.org")
                else "references"
            )
            assigned = entry["category"] + "-" + kind
        entry["subcategory"] = assigned
    used = Counter(e["subcategory"] for e in data["entries"])
    subcategories = [s for s in all_subcategories() if used[s["id"]]]
    suborder = {s["id"]: i for i, s in enumerate(subcategories)}
    data["entries"].sort(key=lambda e: (suborder[e["subcategory"]], e["name"].casefold(), e["url"]))
    fields = [
        "id",
        "name",
        "url",
        "canonicalUrl",
        "description",
        "category",
        "categories",
        "subcategory",
        "stars",
        "starsApproximate",
        "starsAsOf",
        "starsRepository",
    ]
    published = {
        "schemaVersion": 2,
        "repository": data["repository"],
        "collectedAt": data["collectedAt"],
        "statistics": {**data["statistics"], "subcategories": len(subcategories)},
        "categories": data["categories"],
        "subcategories": subcategories,
        "entries": [{key: e[key] for key in fields} for e in data["entries"]],
    }
    (ROOT / "data/entries.json").write_text(
        json.dumps(published, ensure_ascii=False, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                **published["statistics"],
                "starSnapshots": sum(e["stars"] is not None for e in published["entries"]),
            }
        )
    )


if __name__ == "__main__":
    finalize()
