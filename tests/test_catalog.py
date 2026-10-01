import json
import pathlib
import re
from collections import Counter

from scripts.build import readme, report
from scripts.collect import collect
from scripts.deduplicate import canonical_url

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/entries.json").read_text())


def test_resource_identity_and_fields():
    entries = DATA["entries"]
    assert len(entries) == 11066
    assert len({canonical_url(e["url"]) for e in entries}) == len(entries)
    assert len({e["id"] for e in entries}) == len(entries)
    for entry in entries:
        assert all(entry[key] for key in ("name", "url", "description", "category", "subcategory"))
        assert entry["url"].startswith(("http://", "https://"))
        assert entry["canonicalUrl"] == canonical_url(entry["url"])
        assert entry["stars"] is None or isinstance(entry["stars"], int) and entry["stars"] >= 0


def test_normalization_preserves_uncertain_identity():
    assert canonical_url("http://WWW.Example.COM/tool/") == canonical_url(
        "https://example.com/tool"
    )
    assert canonical_url("https://example.com/tool?version=1") != canonical_url(
        "https://example.com/tool?version=2"
    )
    assert canonical_url("https://example.com/File") != canonical_url("https://example.com/file")
    assert canonical_url("https://example.com/page#one") != canonical_url(
        "https://example.com/page#two"
    )


def test_hierarchy_covers_every_entry_without_empty_groups():
    categories = {c["id"] for c in DATA["categories"]}
    subcategories = {s["id"]: s for s in DATA["subcategories"]}
    assert len(subcategories) == len(DATA["subcategories"])
    counts = Counter(e["subcategory"] for e in DATA["entries"])
    for entry in DATA["entries"]:
        assert entry["category"] in categories
        assert subcategories[entry["subcategory"]]["parent"] == entry["category"]
    for sub in subcategories:
        assert counts[sub] > 0
        names = [
            (e["name"].casefold(), e["url"]) for e in DATA["entries"] if e["subcategory"] == sub
        ]
        assert names == sorted(names)


def test_generated_readme_tables_and_anchors_are_complete():
    text = (ROOT / "README.md").read_text()
    assert text == readme(DATA)
    assert (ROOT / "docs/extraction-report.md").read_text() == report(DATA)
    rows = re.findall(r"^\| \[.*?\]\(<(.*?)>\) \|", text, re.M)
    assert Counter(rows) == Counter(e["url"] for e in DATA["entries"])
    for category in DATA["categories"]:
        assert f'id="category-{category["id"]}"' in text
    for sub in DATA["subcategories"]:
        assert f'id="subcategory-{sub["id"]}"' in text
    assert "Sources and credits" not in text


def test_static_artifact_contains_the_complete_collection():
    catalog = json.loads((ROOT / "dist/catalog.json").read_text())
    assert [e["id"] for e in catalog["entries"]] == [e["id"] for e in DATA["entries"]]
    counts = Counter(e["category"] for e in DATA["entries"])
    for category, count in counts.items():
        page = (ROOT / f"dist/categories/{category}.html").read_text()
        assert len(re.findall(r'data-entry="[a-f0-9]+"', page)) == count
        assert not re.search(r"\{\{[A-Z_]+\}\}", page)


def test_full_collection_matches_private_intake_when_available():
    audit = ROOT / ".local/catalog-audit.json"
    if audit.exists():
        original = json.loads(audit.read_text())
        assert {e["canonicalUrl"] for e in original["entries"]} == {
            e["canonicalUrl"] for e in DATA["entries"]
        }
        assert sum(len(e["occurrences"]) for e in original["entries"]) == 43188
        assert len(original["sources"]) == 12


def test_collector_handles_nested_catalogs_and_project_names(tmp_path):
    from scripts.collect import REPOS

    manifest = []
    for repo in REPOS:
        folder = tmp_path / repo.replace("/", "__")
        folder.mkdir()
        files = []
        if repo == REPOS[0]:
            content = "# Resources\n\n- [claude-code-tool](https://github.com/person/claude-code-tool) — A coding tool.\n\n```text\n[Example](https://example.invalid)\n```\n"
            (folder / "README.md").write_text(content)
            files.append({"path": "README.md", "size": len(content)})
            (folder / "data").mkdir()
            content = "title: Build\nsubsections:\n- title: Clients\n  entries:\n  - name: SDK\n    url: https://example.com/sdk\n    description: A real client.\n"
            (folder / "data/build.yaml").write_text(content)
            files.append({"path": "data/build.yaml", "size": len(content)})
        manifest.append(
            {
                "repo": repo,
                "url": "https://github.com/" + repo,
                "sha": "a" * 40,
                "branch": "main",
                "files": files,
            }
        )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    result = collect(tmp_path)
    assert {e["url"] for e in result["occurrences"]} == {
        "https://github.com/person/claude-code-tool",
        "https://example.com/sdk",
    }


def test_collector_uses_individual_html_card_descriptions(tmp_path):
    from scripts.collect import REPOS

    manifest = []
    for repo in REPOS:
        folder = tmp_path / repo.replace("/", "__")
        folder.mkdir()
        files = []
        if repo == REPOS[0]:
            content = '# Gallery\n\n<table>\n<tr><td><a href="https://example.com/one">One</a><br><sub>Author · 2026-10-01</sub><br>First resource.</td></tr>\n<tr><td><a href="https://example.com/two">Two</a><br><sub>Author · 2026-10-01</sub><br>Second resource.</td></tr>\n</table>\n'
            (folder / "README.md").write_text(content)
            files.append({"path": "README.md", "size": len(content)})
        manifest.append(
            {
                "repo": repo,
                "url": "https://github.com/" + repo,
                "sha": "a" * 40,
                "branch": "main",
                "files": files,
            }
        )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    entries = collect(tmp_path)["occurrences"]
    assert len(entries) == 2
    assert "Second resource" not in entries[0]["description"]
    assert "First resource" not in entries[1]["description"]
