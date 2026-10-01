#!/usr/bin/env python3
"""Collect source occurrences without deduplication; never follow resource links.

Install scripts/requirements.txt, then run with a directory containing the twelve
pinned repository snapshots and their manifest.json. The output is an audit input,
not a second editable catalog.
"""

import argparse
import hashlib
import html
import json
import pathlib
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlparse

import yaml
from markdown_it import MarkdownIt

REPOS = [
    "v-modal/awesome-jev-tools",
    "jqueryscript/awesome-jev",
    "onmyway133/awesome-jev",
    "valentynkit/awesome-jev-typesafe",
    "daftAI2026/awesome-jev",
    "ckaraca/awesome-jev",
    "anandi1989/awesome-jev-usecases",
    "JohnDotOwl/awesome-jev",
    "valentynkit/awesome-jev-5",
    "punk2898/awesome-jev-verified",
    "fatwang2/awesome-jev-anotia",
    "Li-Evan/awesome-jev",
]
MD = MarkdownIt("commonmark").enable("table")
POLICY = re.compile(
    r"(^|/)(?:AGENTS\.md|CLAUDE\.md|SKILL\.md|CONTRIBUTING(?:\.[a-z-]+)?\.md|code-of-conduct\.md|LICENSE(?:\.[a-z]+)?|PULL_REQUEST_TEMPLATE\.md)$",
    re.I,
)
POLICY_LINK = re.compile(
    r"(^|/)(?:CONTRIBUTING(?:\.[a-z-]+)?\.md|code-of-conduct\.md|LICENSE(?:\.[a-z]+)?)$", re.I
)
MEDIA = re.compile(r"\.(?:svg|png|jpe?g|gif|webp|mp4|webm|ico)(?:[?#]|$)", re.I)
GENERIC = {
    "repo",
    "github",
    "site",
    "source",
    "code",
    "demo",
    "link",
    "evidence",
    "open",
    "url",
    "view",
    "post",
    "article",
}


def plain(value):
    value = html.unescape(str(value or ""))
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[*`]", "", value)
    return re.sub(r"\s+", " ", value).strip(" |—–-·")


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.current = [attrs["href"], "", self.getpos()[0]]
        if tag == "img" and self.current:
            self.current[1] += attrs.get("alt", "")

    def handle_data(self, data):
        if self.current:
            self.current[1] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current:
            self.links.append(tuple(self.current))
            self.current = None


def collect(root):
    manifest = json.loads((root / "manifest.json").read_text())
    assert [x["repo"] for x in manifest] == REPOS
    occurrences, excluded, files = [], [], []

    def add(
        source, path, location, name, url, description, category, kind="markdown", status="listed"
    ):
        if not isinstance(url, str) or not url.strip():
            return
        original_url = html.unescape(url.strip())
        parsed = urlparse(original_url)
        reason = None
        if original_url.startswith("#"):
            reason = "navigation anchor"
        elif parsed.scheme and parsed.scheme not in ("http", "https"):
            reason = "non-web link"
        elif kind == "markdown" and POLICY_LINK.search(unquote(parsed.path)):
            reason = "repository contribution or license policy"
        elif MEDIA.search(original_url) or any(
            s in original_url
            for s in ["img.shields.io", "opengraph.githubassets.com", "awesome.re"]
        ):
            reason = "decorative media or badge"
        elif parsed.netloc.lower() == "github.com" and parsed.path.startswith(
            "/" + source["repo"] + "/"
        ):
            parts = parsed.path.split("/")
            target = "/".join(parts[5:]) if len(parts) > 5 and parts[3] in ("blob", "tree") else ""
            if len(parts) > 3 and parts[3] in (
                "settings",
                "actions",
                "commits",
                "issues",
                "pulls",
                "compare",
            ):
                reason = "repository administration or contribution navigation"
            elif (
                kind == "markdown"
                and target
                and target.lower().endswith((".md", ".json", ".yaml", ".yml"))
                and (
                    "cheatsheet" not in target.lower()
                    and target.lower() != "skill.md"
                    and not target.startswith(("patterns/", "taxonomy/"))
                )
            ):
                reason = "internal catalog navigation (target file inventoried separately)"
        if not parsed.scheme and not reason:
            rel = pathlib.PurePosixPath(path).parent / original_url.split("#")[0]
            if (
                kind == "markdown"
                and rel.suffix.lower() in (".md", ".json", ".yaml", ".yml")
                and (
                    "cheatsheet" not in str(rel).lower()
                    and rel.name.lower() != "skill.md"
                    and "patterns/" not in str(rel).lower()
                    and "taxonomy/" not in str(rel).lower()
                )
            ):
                reason = "internal catalog navigation (target file inventoried separately)"
            url = urljoin(
                f"https://github.com/{source['repo']}/blob/{source['sha']}/{path}", original_url
            )
        else:
            url = original_url
        if reason:
            excluded.append(
                {
                    "source": source["repo"],
                    "file": path,
                    "location": location,
                    "url": original_url,
                    "reason": reason,
                }
            )
            return
        if not url.startswith(("https://", "http://")):
            return
        name = plain(name)
        if not name or name.lower() in GENERIC:
            bits = urlparse(url)
            name = unquote(bits.path.rstrip("/").split("/")[-1]) or bits.netloc
            if re.fullmatch(r"\d+", name):
                name = plain(description)[:100] or bits.netloc + bits.path
        description = plain(description)
        # Remove the leading resource label and list/table boilerplate, without
        # changing the source's actual descriptive claims.
        if description.startswith(name):
            description = description[len(name) :].strip(" |—–-·:")
        description = re.sub(r"⭐\s*[\d.,]+[kKmM]?|★\s*[\d.,]+[kKmM]?", "", description)
        description = plain(description)
        if not description:
            description = "Listed by the source without a separate description."
        occurrences.append(
            {
                "id": f"o{len(occurrences) + 1:06}",
                "name": name,
                "url": url,
                "originalUrl": original_url,
                "description": description,
                "originalCategory": plain(category) or "Resources",
                "source": source["repo"],
                "file": path,
                "location": location,
                "format": kind,
                "status": status,
            }
        )

    def markdown(source, path, text):
        tokens = MD.parse(text)
        heading = "Resources"
        lines = text.splitlines()
        for i, token in enumerate(tokens):
            if token.type == "heading_open" and i + 1 < len(tokens):
                heading = plain(tokens[i + 1].content)
            if token.type not in ("inline", "html_block"):
                continue
            start = token.map[0] if token.map else 0
            content = token.content
            # A table cell's own token map is absent. Its containing row is the
            # nearest mapped token; retain that row for the description.
            if not token.map:
                parent = next((t for t in reversed(tokens[:i]) if t.map), None)
                if parent and parent.map:
                    start = parent.map[0]
            line = lines[start] if start < len(lines) else content
            description = line if line.lstrip().startswith("|") else content
            children = token.children or []
            seen = set()
            for j, child in enumerate(children):
                if child.type != "link_open":
                    continue
                href = child.attrGet("href")
                label = []
                has_image = False
                for following in children[j + 1 :]:
                    if following.type == "link_close":
                        break
                    if following.type == "image":
                        has_image = True
                    if following.type in ("text", "code_inline"):
                        label.append(following.content)
                if has_image and not label:
                    excluded.append(
                        {
                            "source": source["repo"],
                            "file": path,
                            "location": start + 1,
                            "url": href,
                            "reason": "linked badge or image",
                        }
                    )
                    continue
                add(source, path, start + 1, "".join(label), href, description, heading)
                seen.add(href)
            if token.type == "html_block" or any(c.type == "html_inline" for c in children):
                # Generated gallery tables can occupy one very large AST block.
                # Each row is one resource card; never use the entire gallery as
                # an individual resource description.
                rows = list(re.finditer(r"<tr\b[^>]*>.*?</tr>", content, re.S | re.I))
                blocks = [(m.group(), content[: m.start()].count("\n")) for m in rows] or [
                    (content, 0)
                ]
                for block, offset in blocks:
                    parser = Anchors()
                    parser.feed(block)
                    details = re.search(r"</sub>\s*<br\s*/?>(.*)", block, re.S | re.I)
                    desc = details.group(1) if details else block
                    desc = re.split(r"<(?:br\s*/?>)?\s*<sub>Also:", desc, flags=re.I)[0]
                    desc = re.sub(r"<sub>Also:.*?</sub>", "", desc, flags=re.S | re.I)
                    desc = plain(desc)
                    for href, label, local_line in parser.links:
                        add(source, path, start + offset + local_line, label, href, desc, heading)
                        seen.add(href)
            # Preserve unformatted resource URLs in prose and research notes;
            # fenced code and inline code examples are excluded by construction.
            raw_prose = " ".join(c.content for c in children if c.type == "text")
            for match in re.finditer(r'https?://[^\s<>\]"\)]+', raw_prose):
                href = match.group().rstrip(".,;")
                if href not in seen:
                    add(source, path, start + 1, "", href, description, heading)

    def structured(source, path, obj):
        def walk(node, pointer="", inherited="Resources"):
            if isinstance(node, list):
                for i, value in enumerate(node):
                    walk(value, pointer + "/" + str(i), inherited)
                return
            if not isinstance(node, dict):
                return
            category = (
                node.get("category") or node.get("section") or node.get("title")
                if "entries" in node
                else node.get("category") or node.get("section") or inherited
            )
            if isinstance(category, dict):
                category = category.get("en") or inherited
            category = str(category or inherited)
            desc = node.get("description") or node.get("desc") or node.get("summary") or ""
            if isinstance(desc, dict):
                desc = desc.get("en") or next(iter(desc.values()), "")
            name = (
                node.get("name")
                or node.get("title")
                or node.get("repo")
                or node.get("full_name")
                or ""
            )
            urls = []
            for key in [
                "url",
                "repo_url",
                "site_url",
                "post_url",
                "originalUrl",
                "aihotUrl",
                "site",
                "homepage",
            ]:
                if isinstance(node.get(key), str) and node[key].startswith(("http://", "https://")):
                    urls.append((key, node[key]))
            if (
                isinstance(node.get("repo"), str)
                and "/" in node["repo"]
                and not node["repo"].startswith("http")
            ):
                u = "https://github.com/" + node["repo"]
                if u not in [v for _, v in urls]:
                    urls.append(("repo", u))
            status = (
                "unreviewed source lead"
                if path.endswith("leads.json")
                else "unselected source news"
                if node.get("selected") is False
                else "listed"
            )
            for key, url in urls:
                add(
                    source,
                    path,
                    pointer + "/" + key,
                    name,
                    url,
                    desc,
                    category,
                    "structured",
                    status,
                )
            # Metadata caches keyed by owner/repository still enumerate resources.
            if path == "data/github.json" and isinstance(node.get("repos"), dict):
                for repo, meta in node["repos"].items():
                    add(
                        source,
                        path,
                        pointer + "/repos/" + repo,
                        repo,
                        "https://github.com/" + repo,
                        meta.get("description", ""),
                        "Repository metadata",
                        "structured",
                    )
                    if meta.get("homepage"):
                        add(
                            source,
                            path,
                            pointer + "/repos/" + repo + "/homepage",
                            repo + " website",
                            meta["homepage"],
                            meta.get("description", ""),
                            "Repository metadata",
                            "structured",
                        )
                return
            for key, value in node.items():
                if key in ("links",):
                    if isinstance(value, dict):
                        for label, href in value.items():
                            if isinstance(href, str):
                                add(
                                    source,
                                    path,
                                    pointer + "/" + key + "/" + label,
                                    str(name) + " — " + label,
                                    href,
                                    desc,
                                    category,
                                    "structured",
                                    status,
                                )
                elif key in (
                    "entries",
                    "projects",
                    "items",
                    "sections",
                    "subsections",
                    "gallery",
                    "evidence",
                    "sourceMeta",
                    "inclusion",
                ):
                    walk(value, pointer + "/" + key, category)

        walk(obj)

    for source in manifest:
        folder = root / source["repo"].replace("/", "__")
        processed = []
        for item in sorted(source["files"], key=lambda x: x["path"]):
            path = item["path"]
            p = folder / path
            role = "implementation, policy, media, or generated site asset"
            if (
                path.lower().endswith(".md")
                and not POLICY.search(path)
                and not path.startswith(
                    (".github/", ".grok/", "scripts/", "src/", "tools/", "docs/superpowers/")
                )
                and not (source["repo"] == "daftAI2026/awesome-jev" and path.startswith("docs/"))
            ):
                before = len(occurrences)
                markdown(source, path, p.read_text())
                role = "resource document"
            elif (
                path.startswith(("data/", "catalog/", "docs/data/"))
                and path.endswith((".json", ".yaml", ".yml"))
                and not any(x in path for x in ["/i18n/", "/stars/"])
                and pathlib.Path(path).name not in ["history.json", "jev.json", "sections.yaml"]
            ):
                before = len(occurrences)
                obj = (
                    json.loads(p.read_text())
                    if path.endswith(".json")
                    else yaml.safe_load(p.read_text())
                )
                structured(source, path, obj)
                role = "structured resource catalog"
            else:
                files.append(
                    {
                        "source": source["repo"],
                        "file": path,
                        "role": role,
                        "bytes": p.stat().st_size,
                    }
                )
                continue
            processed.append(path)
            files.append(
                {
                    "source": source["repo"],
                    "file": path,
                    "role": role,
                    "bytes": p.stat().st_size,
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                    "occurrences": len(occurrences) - before,
                }
            )
        source["processedFiles"] = processed
        source.pop("files", None)
    return {
        "sources": manifest,
        "occurrences": occurrences,
        "excludedLinks": excluded,
        "fileInventory": files,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshots", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    result = collect(args.snapshots)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "sources": len(result["sources"]),
                "occurrences": len(result["occurrences"]),
                "excludedLinks": len(result["excludedLinks"]),
                "processedFiles": sum(len(s["processedFiles"]) for s in result["sources"]),
            }
        )
    )
