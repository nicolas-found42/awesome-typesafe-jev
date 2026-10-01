"""Regression checks for contextual metadata on nested resource links."""

import json

from scripts.collect import REPOS, collect


def test_nested_readme_links_keep_project_context_without_cross_contamination(tmp_path):
    manifest = []
    for repo in REPOS:
        folder = tmp_path / repo.replace("/", "__")
        folder.mkdir()
        files = []
        if repo == REPOS[0]:
            (folder / "data").mkdir()
            records = [
                {
                    "title": "Watchdog",
                    "url": "https://github.com/example/watchdog",
                    "summary": "Monitors coding-agent trajectories.",
                    "sourceMeta": {
                        "inclusion": {
                            "text": {
                                "en": "Uses Jev to judge quarantine decisions.",
                                "ja": "日本語",
                            },
                            "evidence": [
                                {
                                    "url": "https://github.com/example/watchdog/blob/abc/README.md",
                                    "quote": "Jev is the default judge.",
                                }
                            ],
                        }
                    },
                },
                {
                    "title": "Skill picker",
                    "url": "https://github.com/example/skills",
                    "summary": "Chooses an installed agent skill.",
                    "sourceMeta": {
                        "inclusion": {
                            "evidence": [
                                {"url": "https://github.com/example/skills/blob/def/README.md"}
                            ]
                        }
                    },
                },
            ]
            text = json.dumps(records)
            (folder / "data/github.json").write_text(text)
            files.append({"path": "data/github.json", "size": len(text)})
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
    readmes = [e for e in entries if e["url"].endswith("/README.md")]
    assert [(e["name"], e["description"]) for e in readmes] == [
        ("Watchdog — README", "Uses Jev to judge quarantine decisions."),
        ("Skill picker — README", "Chooses an installed agent skill."),
    ]


def test_published_documentation_has_project_names_and_real_descriptions():
    from pathlib import Path

    data = json.loads((Path(__file__).resolve().parents[1] / "data/entries.json").read_text())
    assert not [entry["url"] for entry in data["entries"] if entry["name"] == "README.md"]
    examples = {
        "glebmish/jev-watchdog": "default judge",
        "goodruizhan/pi-jev-control": "Pi Coding Agent",
        "govindup63/skillpick": "installed coding-agent skill",
        "grizzlypeaksoftware/jev-demo": "tool-call guard",
        "guhan-tofu/system-one-plus-two-ops-agent": "in-memory mocks",
    }
    for repository, phrase in examples.items():
        entry = next(
            e
            for e in data["entries"]
            if repository + "/blob/" in e["url"] and e["url"].endswith("/README.md")
        )
        assert entry["name"].endswith(" — README")
        assert phrase in entry["description"]
