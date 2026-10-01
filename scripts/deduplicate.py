#!/usr/bin/env python3
"""Merge exact resource identities using the user's explicit URL rules."""

import hashlib
import json
import pathlib
import sys
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit


def canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    authority = host + (f":{parsed.port}" if parsed.port is not None else "")
    return urlunsplit(("https", authority, parsed.path.rstrip("/"), parsed.query, parsed.fragment))


def english_fraction(value: str) -> float:
    letters = [c for c in value if c.isalpha()]
    return sum(c.isascii() for c in letters) / max(1, len(letters))


def description_quality(occurrence):
    text = occurrence["description"]
    return (
        text != "Listed by the source without a separate description.",
        english_fraction(text) > 0.7,
        "|" not in text,
        "http" not in text,
        occurrence["format"] == "structured",
        len(text.split()),
        len(text),
    )


def merge(collection):
    groups = defaultdict(list)
    for occurrence in collection["occurrences"]:
        groups[canonical_url(occurrence["url"])].append(occurrence)
    entries = []
    for identity, occurrences in groups.items():
        descriptive = max(occurrences, key=description_quality)
        names = sorted(
            occurrences,
            key=lambda o: (
                english_fraction(o["name"]) > 0.7,
                len(o["name"]) <= 120,
                o["format"] == "structured",
                o["description"] != "Listed by the source without a separate description.",
                o["name"] == descriptive["name"],
                -len(o["name"]),
            ),
            reverse=True,
        )
        entries.append(
            {
                "id": hashlib.sha256(identity.encode()).hexdigest()[:16],
                "name": names[0]["name"],
                "url": descriptive["url"],
                "canonicalUrl": identity,
                "description": descriptive["description"],
                "descriptionOccurrence": descriptive["id"],
                "sources": sorted(set(o["source"] for o in occurrences)),
                "originalCategories": sorted(set(o["originalCategory"] for o in occurrences)),
                "occurrences": occurrences,
            }
        )
    assert sum(len(e["occurrences"]) for e in entries) == len(collection["occurrences"])
    assert len({e["canonicalUrl"] for e in entries}) == len(entries)
    return {
        **{k: v for k, v in collection.items() if k != "occurrences"},
        "entries": entries,
        "statistics": {
            "beforeDeduplication": len(collection["occurrences"]),
            "afterDeduplication": len(entries),
            "duplicatesMerged": len(collection["occurrences"]) - len(entries),
        },
    }


if __name__ == "__main__":
    result = merge(json.loads(pathlib.Path(sys.argv[1]).read_text()))
    pathlib.Path(sys.argv[2]).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["statistics"]))
