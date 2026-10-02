#!/usr/bin/env python3
"""Generate every public catalog artifact from data/entries.json."""

import html
import json
import pathlib
import re
import shutil
from collections import Counter
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]


def md_text(value):
    return re.sub(r"([\\`*\[\]<>_|])", r"\\\1", value)


def escape(value):
    return html.escape(str(value), quote=True)


def stars(entry):
    if entry["stars"] is None:
        return "—"
    return ("≈" if entry["starsApproximate"] else "") + f"{entry['stars']:,}"


def read_data():
    return json.loads((ROOT / "data/entries.json").read_text())


def readme(data):
    repo = data["repository"]
    counts = Counter(e["category"] for e in data["entries"])
    subcounts = Counter(e["subcategory"] for e in data["entries"])
    lines = [
        f"# {repo['name']}",
        "",
        "Tools, libraries, applications, articles and experiments for building with TypeSafe’s Jev.",
        "",
        f"**[Explore Jev Atlas →]({repo['siteUrl']})** · "
        "[Download the catalog](data/entries.json) · [Contribute](#contributing)",
        "",
        f"**{len(data['entries']):,} resources · {len(data['categories'])} categories · "
        f"{len(data['subcategories'])} subcategories · Updated {data['collectedAt']}**",
        "",
        "Search names and descriptions, browse focused subcategories, sort by repository stars, "
        "switch between tables and cards, and save a personal reading list. "
        "Share a filtered URL or browse complete static category pages without JavaScript.",
        "",
        "Repository stars are imported snapshots, not live counts. “≈” marks a rounded count; "
        "“—” means unavailable. A source-file link shows the stars of its containing repository. "
        "Descriptions are informational; inclusion is not an endorsement.",
        "",
        "## Contents",
        "",
    ]
    for category in data["categories"]:
        lines.append(
            f"- [{category['name']} ({counts[category['id']]:,})](#category-{category['id']})"
        )
        for sub in data["subcategories"]:
            if sub["parent"] == category["id"]:
                lines.append(
                    f"  - [{sub['name']} ({subcounts[sub['id']]:,})](#subcategory-{sub['id']})"
                )
    lines += [
        "- [Contributing](#contributing)",
        "- [Build and verification](#build-and-verification)",
        "",
    ]
    for category in data["categories"]:
        lines += [
            f'<details id="category-{category["id"]}">',
            f"<summary><strong>{escape(category['name'])}</strong> · {counts[category['id']]:,} resources</summary>",
            "",
        ]
        for sub in data["subcategories"]:
            if sub["parent"] != category["id"]:
                continue
            lines += [
                f'<details id="subcategory-{sub["id"]}">',
                f"<summary><strong>{escape(sub['name'])}</strong> · {subcounts[sub['id']]:,} resources</summary>",
                "",
                "| Resource | Repository stars | Description |",
                "| :--- | ---: | :--- |",
            ]
            for entry in data["entries"]:
                if entry["subcategory"] == sub["id"]:
                    lines.append(
                        f"| [{md_text(entry['name'])}](<{entry['url']}>) | "
                        f"{stars(entry)} | {md_text(entry['description'])} |"
                    )
            lines += ["", "</details>", ""]
        lines += ["</details>", ""]
    lines += [
        "## Contributing",
        "",
        "1. Add or correct a resource in `data/entries.json`. Include its name, real URL, "
        "description, category and subcategory. Keep uncertain duplicate identities separate.",
        "2. Provide evidence for the entry in your pull request. Preserve the full existing collection.",
        "3. Set `stars` to `null` when no repository star snapshot is available. "
        "Never present a missing count as zero, and date any supplied snapshot.",
        "4. Run the generator and validation commands below. "
        "The README and website are generated from the same data file.",
        "5. Open a pull request, or use GitHub Issues to suggest corrections.",
        "",
        "## Build and verification",
        "",
        "```sh",
        "uv sync --locked",
        "npm ci",
        "uv run python scripts/build.py",
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run ty check",
        "uv run pytest",
        "npm test",
        "actionlint",
        "```",
        "",
        "The canonical data file is the only editable catalog. The README, static website "
        "and category pages are generated outputs. See [maintenance instructions](docs/maintenance.md).",
        "",
        f"GitHub Actions deploys every push to `main` to [{repo['siteUrl']}]({repo['siteUrl']}). "
        "Pull requests run validation without deployment.",
        "",
    ]
    return "\n".join(lines)


def resource_table(entries, sub_lookup, category_lookup):
    rows = []
    for entry in entries:
        label = category_lookup[entry["category"]]["name"]
        sublabel = sub_lookup[entry["subcategory"]]["name"]
        rows.append(
            f'<tr class="resource-item" data-entry="{entry["id"]}">'
            f'<td class="resource-name"><a class="resource-link" href="{escape(entry["url"])}">{escape(entry["name"])}</a>'
            f'<span class="resource-host">{escape(urlsplit(entry["url"]).hostname)}</span></td>'
            f'<td class="stars-cell" data-label="Stars" title="Repository star snapshot; not live">{stars(entry)}</td>'
            f'<td class="description-cell">{escape(entry["description"])}</td>'
            f'<td class="category-cell"><span>{escape(label)}</span><small>{escape(sublabel)}</small></td>'
            '<td class="save-cell"><span class="static-save" aria-hidden="true">♡</span></td></tr>'
        )
    return (
        '<table class="resource-table"><caption class="sr-only">Resources, repository stars, descriptions and categories</caption><thead><tr><th scope="col">Resource</th><th scope="col">Stars</th><th scope="col">Description</th><th scope="col">Category</th><th scope="col"><span class="sr-only">Save</span></th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table>"
    )


def grouped_tables(items, matching, sub_lookup, category_lookup):
    """Keep every row inside native category and subcategory disclosures."""
    category_counts = Counter(e["category"] for e in matching)
    sub_counts = Counter(e["subcategory"] for e in matching)
    grouped = {}
    for entry in items:
        grouped.setdefault(entry["category"], {}).setdefault(entry["subcategory"], []).append(entry)
    parts = []
    for category, groups in grouped.items():
        shown = sum(len(group) for group in groups.values())
        parts.append(
            f'<details class="result-category" id="category-{category}" open>'
            f"<summary><span>{escape(category_lookup[category]['name'])}</span>"
            f'<span class="group-count">{shown:,} of {category_counts[category]:,} matches</span></summary>'
            '<div class="category-content">'
        )
        for sub, group in groups.items():
            parts.append(
                f'<details class="result-subcategory" id="subcategory-{sub}" open>'
                f"<summary><span>{escape(sub_lookup[sub]['name'])}</span>"
                f'<span class="group-count">{len(group):,} of {sub_counts[sub]:,} matches</span></summary>'
                + resource_table(group, sub_lookup, category_lookup)
                + "</details>"
            )
        parts.append("</div></details>")
    return "".join(parts)


def website(data):
    destination = ROOT / "dist"
    if destination.exists():
        shutil.rmtree(destination)
    (destination / "assets").mkdir(parents=True)
    (destination / "categories").mkdir()
    (destination / "data").mkdir()
    for name in ["style.css", "app.js", "theme.js", "favicon.svg"]:
        shutil.copyfile(ROOT / "site" / name, destination / "assets" / name)
    shutil.copyfile(ROOT / "data/entries.json", destination / "data/entries.json")
    (destination / ".nojekyll").write_text("")
    entries = [
        {
            k: e[k]
            for k in [
                "id",
                "name",
                "url",
                "description",
                "category",
                "subcategory",
                "stars",
                "starsApproximate",
                "starsAsOf",
            ]
        }
        for e in data["entries"]
    ]
    catalog = {
        "categories": data["categories"],
        "subcategories": data["subcategories"],
        "entries": entries,
        "collectedAt": data["collectedAt"],
    }
    (destination / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + "\n"
    )
    template = (ROOT / "site/index.html").read_text()
    category_lookup = {c["id"]: c for c in data["categories"]}
    sub_lookup = {s["id"]: s for s in data["subcategories"]}
    counts = Counter(e["category"] for e in data["entries"])
    subcounts = Counter(e["subcategory"] for e in data["entries"])
    domains = len({urlsplit(e["url"]).hostname for e in entries})

    def page(default="all"):
        base = "./" if default == "all" else "../"
        selected = (
            data["entries"]
            if default == "all"
            else [e for e in data["entries"] if e["category"] == default]
        )
        initial = sorted(
            selected,
            key=lambda e: (
                -(e["stars"] if e["stars"] is not None else -1),
                e["name"].casefold(),
                e["url"],
            ),
        )[:48]
        shown = selected if default != "all" else initial
        initial_markup = grouped_tables(shown, selected, sub_lookup, category_lookup)
        initial_count = len(shown)
        nav = []
        for category in data["categories"]:
            identifier = category["id"]
            nav.append(
                f'<details class="nav-group" data-parent="{identifier}"'
                + (" open" if identifier == default else "")
                + "><summary><span>"
                + escape(category["name"])
                + f'</span><span class="nav-count">{counts[identifier]:,}</span></summary>'
            )
            nav.append(
                f'<a class="category-link" data-category="{identifier}" href="{base}categories/{identifier}.html#results"><span>All in this category</span><span class="nav-count">{counts[identifier]:,}</span></a>'
            )
            for sub in data["subcategories"]:
                if sub["parent"] == identifier:
                    nav.append(
                        f'<a class="subcategory-link" data-category="{identifier}" data-subcategory="{sub["id"]}" href="{base}categories/{identifier}.html#subcategory-{sub["id"]}"><span>{escape(sub["name"])}</span><span class="nav-count">{subcounts[sub["id"]]:,}</span></a>'
                    )
            nav.append("</details>")
        replacements = {
            "BASE": base,
            "ENTRY_COUNT": f"{len(entries):,}",
            "CATEGORY_COUNT": str(len(data["categories"])),
            "SUBCATEGORY_COUNT": str(len(data["subcategories"])),
            "DOMAIN_COUNT": f"{domains:,}",
            "SNAPSHOT_DATE": data["collectedAt"],
            "DEFAULT_CATEGORY": default,
            "PAGE_TITLE": "The TypeSafe & Jev resource directory"
            if default == "all"
            else category_lookup[default]["name"],
            "CANONICAL": data["repository"]["siteUrl"]
            + ("" if default == "all" else "categories/" + default + ".html"),
            "CATEGORY_NAV": "".join(nav),
            "CATEGORY_OPTIONS": "".join(
                f'<option value="{c["id"]}">{escape(c["name"])} ({counts[c["id"]]:,})</option>'
                for c in data["categories"]
            ),
            "INITIAL_ENTRIES": initial_markup,
            "INITIAL_COUNT": f"{len(selected):,} of {len(entries):,} resources",
            "PAGE_STATUS": f"Showing {initial_count:,} of {len(selected):,} resources",
        }
        output = template
        for key, value in replacements.items():
            output = output.replace("{{" + key + "}}", str(value))
        if re.search(r"\{\{[A-Z_]+\}\}", output):
            raise ValueError("Unresolved template token")
        return output

    (destination / "index.html").write_text(page())
    for category in data["categories"]:
        (destination / "categories" / (category["id"] + ".html")).write_text(page(category["id"]))
    about = f"""<!doctype html><html lang="en" data-theme="auto"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><title>About · Jev Atlas</title><link rel="stylesheet" href="assets/style.css"><link rel="icon" href="assets/favicon.svg"><script src="assets/theme.js"></script></head><body><header class="site-header"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">j<span>↗</span></span><span>Jev <strong>Atlas</strong><small>TypeSafe &amp; System One</small></span></a><div class="header-actions"><a class="header-link" href="https://github.com/nicolas-found42/awesome-typesafe-jev">GitHub ↗</a><button id="theme-toggle" class="icon-button" type="button" aria-label="Change theme">◐</button></div></header><main class="prose-page"><span class="eyebrow">A DIRECTORY FOR YOUR NEXT BUILD</span><h1>Explore what typed decisions can do.</h1><p>Jev Atlas brings {len(entries):,} tools, libraries, applications, articles and experiments into one searchable directory. Browse {len(data["categories"])} categories and {len(data["subcategories"])} focused subcategories, or search for the problem you want to solve.</p><div class="audit-callout"><strong>Make the collection yours.</strong><p>Save resources to a personal reading list, switch between table and card views, or share your search with a filtered URL. Saved resources stay in your browser.</p></div><h2>Reading the directory</h2><ul><li>Each entry links to its original resource and carries an informational description.</li><li>Stars are repository snapshots imported on {data["collectedAt"]}; the underlying metadata may be older. They are not live counts. “≈” indicates a rounded count and “—” indicates unavailable data.</li><li>When an entry points to a file inside a repository, the star count belongs to the containing repository.</li><li>Entries without enough information for a precise topic are grouped by resource format, such as projects, discussions or reference pages.</li><li>Inclusion does not establish security, accuracy, profitability or production readiness.</li></ul><h2>Browse your way</h2><p>Search names and descriptions, combine category and subcategory filters, sort by stars, and use the nested menu to explore. Press <kbd>/</kbd> to focus search. The directory follows your system theme; the header toggle cycles through system, light and dark.</p><h2>Contribute a correction</h2><p><a href="https://github.com/nicolas-found42/awesome-typesafe-jev/issues">Report an issue</a> or propose a change to the <a href="https://github.com/nicolas-found42/awesome-typesafe-jev">repository</a>. The website and README are generated from one <a href="data/entries.json">structured catalog</a>.</p><p><a href="index.html">← Return to the directory</a></p></main></body></html>"""
    (destination / "about.html").write_text(about)
    urls = [data["repository"]["siteUrl"], data["repository"]["siteUrl"] + "about.html"] + [
        data["repository"]["siteUrl"] + "categories/" + c["id"] + ".html"
        for c in data["categories"]
    ]
    (destination / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join("<url><loc>" + escape(url) + "</loc></url>" for url in urls)
        + "</urlset>\n"
    )
    (destination / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + data["repository"]["siteUrl"] + "sitemap.xml\n"
    )


def report(data):
    stats = data["statistics"]
    return f"""# Import and generation checks

| Measure | Count |
| :--- | ---: |
| Resource occurrences collected | {stats["beforeDeduplication"]:,} |
| Repeated occurrences merged | {stats["duplicatesMerged"]:,} |
| Unique resources retained | {stats["afterDeduplication"]:,} |
| Categories | {stats["categories"]} |
| Subcategories | {stats["subcategories"]} |
| Resources with star snapshots | {sum(e["stars"] is not None for e in data["entries"]):,} |

URL identity normalizes HTTP/HTTPS, optional www, domain letter case and trailing slashes. Paths, queries and fragments remain intact when identity is uncertain.

The complete collection is retained. Descriptions and stars are imported metadata, not independently verified product claims. Semantic subcategory judgments use Jev; uncertain judgments use deterministic resource-format groups. No browser requests to an AI service are required.

The single catalog at `data/entries.json` generates the README, browser data and all static category pages. Detailed intake evidence is retained locally outside the published directory.
"""


if __name__ == "__main__":
    data = read_data()
    (ROOT / "README.md").write_text(readme(data))
    (ROOT / "docs/extraction-report.md").write_text(report(data))
    website(data)
    print(
        f"Generated {len(data['entries']):,} resources, {len(data['categories'])} categories and {len(data['subcategories'])} subcategories in README and static website."
    )
