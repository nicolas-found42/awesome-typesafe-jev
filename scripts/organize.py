#!/usr/bin/env python3
"""Apply reviewed source-category mappings, retaining ambiguity explicitly."""

import json
import pathlib
import re
import sys
from collections import Counter

CATEGORIES = [
    (
        "start",
        "Getting started & official resources",
        "First-party product sites, official API documentation, introductions, quick starts, launch announcements, console and official resources. Excludes community tutorials and benchmarks.",
    ),
    (
        "sdks",
        "SDKs & client libraries",
        "Language SDKs and API client libraries, including official and community clients. Example: Python or Go SDK. Excludes frameworks and gateways.",
    ),
    (
        "integrations",
        "Frameworks & integrations",
        "Framework adapters, platform integrations, automation integrations and reusable development infrastructure. Example: Vercel AI SDK adapter. Excludes language clients and API gateways.",
    ),
    (
        "access",
        "Model access & gateways",
        "Hosted model access, API gateways, providers, deployment and request proxies. Example: OpenRouter or Cloudflare model access. Excludes open model replications.",
    ),
    (
        "observability",
        "Observability & operations",
        "Tracing, monitoring, logging, costs, deployment operations and infrastructure observability. Excludes evaluation benchmarks and application examples.",
    ),
    (
        "agents",
        "Agents & orchestration",
        "General agent harnesses, orchestration, task routing, context management and autonomous workflows. Excludes specifically coding agents, browser use, MCP servers and safety gates.",
    ),
    (
        "skills",
        "MCP servers & agent skills",
        "MCP servers, agent skill packs, plugins and integrations explicitly packaged as MCP or skills. Takes precedence over generic agents when the section is explicitly MCP or skills.",
    ),
    (
        "coding",
        "Coding & developer tools",
        "Coding agents, code review, command line developer tools, semantic code search, git workflows, CI and developer productivity. Excludes general client SDKs.",
    ),
    (
        "browser",
        "Browser, mobile & computer use",
        "Browser automation, computer use, GUI interaction and mobile device automation. Excludes physical robotics.",
    ),
    (
        "robotics",
        "Robotics & simulation",
        "Physical robotics, drone control, embodied agents and robotic simulation. Excludes ordinary games.",
    ),
    (
        "search",
        "Search, retrieval & RAG",
        "Document retrieval, search relevance, reranking, RAG and knowledge search. Excludes semantic code search and general data labeling.",
    ),
    (
        "safety",
        "Safety, moderation & guardrails",
        "Prompt injection defense, tool gating, permissions, moderation, policy enforcement and output verification. Excludes benchmark studies of safety.",
    ),
    (
        "data",
        "Data, classification & extraction",
        "Data processing, classification, labeling, extraction, SQL and data pipelines. Excludes measured model evaluation and retrieval search.",
    ),
    (
        "benchmarks",
        "Benchmarks & evaluation",
        "Measured accuracy, latency, calibration, evaluation harnesses, benchmark datasets and model comparisons. Takes precedence over generic research when testing or metrics are central.",
    ),
    (
        "models",
        "Open models & compatible servers",
        "Open implementations, replicas, model training, inference servers and compatible System One models. Excludes hosted provider access and benchmarks alone.",
    ),
    (
        "games",
        "Games & interactive worlds",
        "Game playing, gaming demos, game agents and playful interactive worlds. Excludes robotics and generic technical playgrounds.",
    ),
    (
        "finance",
        "Finance & trading",
        "Financial analysis, trading, signals, financial automation and markets. Excludes general commerce.",
    ),
    (
        "apps",
        "Applications & productivity",
        "General user applications, email, notes, calendars, personal productivity and broad application categories. Excludes specialized commerce, voice, legal or health applications.",
    ),
    (
        "commerce",
        "Commerce & marketing",
        "Shopping, commerce, marketing, advertising and e-commerce use cases. Excludes customer service and sales support.",
    ),
    (
        "support",
        "Customer support & sales",
        "Customer support, sales support, ticket routing, customer communication and support workflows. Excludes general email productivity.",
    ),
    (
        "science",
        "Legal, health & science",
        "Legal analysis, healthcare, medical, scientific and professional-domain applications. Excludes generic model research and benchmark studies.",
    ),
    (
        "creative",
        "Writing, media & creative tools",
        "Writing, media, visual design, music and creative applications. Excludes general developer tooling.",
    ),
    (
        "voice",
        "Voice & real-time interfaces",
        "Speech, voice assistants, audio interaction and real-time communication interfaces. Excludes general games or other low-latency examples.",
    ),
    (
        "education",
        "Education & teaching",
        "Educational applications and teaching use cases. Excludes articles that teach developers how to use Jev; those belong to learning.",
    ),
    (
        "demos",
        "Demos & playgrounds",
        "General-purpose technical demos, interactive API playgrounds and examples when no specific domain is given. Excludes explicit games and official vendor console.",
    ),
    (
        "patterns",
        "Decision patterns & architecture",
        "Reusable decision patterns: routing, scoring, verification, bulk labeling, confidence handling and architecture recipes. Excludes actual implemented tools and measured benchmarks.",
    ),
    (
        "learning",
        "Articles, tutorials & talks",
        "Learning resources, guides, tutorials, videos, talks, discussions, critique, research writeups and general news. Excludes official API docs and measured benchmarks.",
    ),
    (
        "community",
        "Community & resource lists",
        "Other awesome lists, curated collections, community accounts, community channels and broader resource directories. Excludes standalone technical projects.",
    ),
    (
        "other",
        "Other resources & source leads",
        "Unclear source categories, miscellaneous experiments, metadata-only records and unreviewed source leads. A broad fallback; use only when another category cannot be justified from the source label.",
    ),
]

FILE_CATEGORIES = {
    "agents": "agents",
    "agent": "agents",
    "browser": "browser",
    "coding": "coding",
    "commerce": "commerce",
    "creative": "creative",
    "data": "data",
    "education": "education",
    "finance": "finance",
    "games": "games",
    "game": "games",
    "getting-started": "start",
    "legal-health": "science",
    "open-models": "models",
    "other": "other",
    "productivity": "apps",
    "robotics": "robotics",
    "safety": "safety",
    "search": "search",
    "support": "support",
    "voice": "voice",
    "app": "apps",
    "context": "agents",
    "guardrail": "safety",
    "infra": "integrations",
    "list": "community",
    "official": "start",
    "repro": "models",
    "research": "benchmarks",
    "retrieval": "search",
    "sdk": "sdks",
}


def category_rule(occurrence):
    """Use explicit source-file roles and literal heading aliases for uncertain labels."""
    path = occurrence["file"]
    stem = pathlib.PurePosixPath(path).stem
    if path == "data/news.json":
        return "learning"
    if path.startswith(("scenarios/", "zh-CN/scenarios/", "categories/")) or path.endswith(".yaml"):
        if stem in FILE_CATEGORIES:
            return FILE_CATEGORIES[stem]
    label = occurrence["originalCategory"].casefold()
    exact = {
        "research": "benchmarks",
        "resources": "learning",
        "references": "learning",
        "alternatives": "models",
        "app": "apps",
        "apps": "apps",
        "applications": "apps",
        "agent": "agents",
        "sdk": "sdks",
        "list": "community",
        "lists": "community",
        "official": "start",
        "context": "agents",
        "tip": "learning",
    }
    if label in exact:
        return exact[label]
    rules = [
        (r"\bmcp\b|\bskills?\b", "skills"),
        (r"\bsdks?\b|\bclients?\b", "sdks"),
        (r"\bdata\b|\bclassification\b|\bextraction\b", "data"),
        (r"\bbenchmarks?\b|\bevaluations?\b|\bcalibration\b", "benchmarks"),
        (r"\bopen models\b|\breplica(?:s|tions)?\b", "models"),
        (r"\bcoding\b|\bdeveloper tools\b|\bdev tooling\b|^claude code$|^codex$", "coding"),
        (r"\bagents?\b|\bcontext\b|\borchestration\b", "agents"),
        (r"\bbrowser\b|\bcomputer use\b|\bmobile\b", "browser"),
        (r"\brobotics\b|\bsimulation\b", "robotics"),
        (r"\bgames?\b", "games"),
        (r"\bapplications?\b|\bapps\b", "apps"),
        (r"\bframeworks?\b|\bintegrations?\b|\binfra\b", "integrations"),
        (r"\bgateways?\b", "access"),
        (r"\blists?\b|\bcommunity\b|\bawesome\b", "community"),
        (r"\bcookbooks?\b|\bpatterns?\b|\bscoring\b|\brouting\b", "patterns"),
        (
            r"\barticles?\b|\bguides?\b|\btutorials?\b|\bthreads?\b|\bdiscussions?\b|\btechniques\b",
            "learning",
        ),
        (r"\bofficial\b|\bgetting started\b|\bannouncements?\b", "start"),
        (r"\bdemos?\b|\bexamples?\b", "demos"),
    ]
    return next((category for pattern, category in rules if re.search(pattern, label)), "other")


def apply_categories(collection, mapping):
    valid = {c[0] for c in CATEGORIES}
    for entry in collection["entries"]:
        votes = Counter()
        for occurrence in entry["occurrences"]:
            category = mapping.get(occurrence["originalCategory"], {}).get("category", "other")
            if category == "other":
                category = category_rule(occurrence)
            if category not in valid:
                raise ValueError(category)
            # Source repositories vote once per category, avoiding translated or
            # generated copies artificially dominating the choice.
            votes[(occurrence["source"], category)] = 1
        tally = Counter(category for _, category in votes if category != "other")
        category_order = {c[0]: i for i, c in enumerate(CATEGORIES)}
        chosen = max(tally, key=lambda c: (tally[c], -category_order[c])) if tally else "other"
        entry["category"] = chosen
        entry["categories"] = [c[0] for c in CATEGORIES if c[0] in tally] or ["other"]
    order = {c[0]: i for i, c in enumerate(CATEGORIES)}
    collection["entries"].sort(key=lambda e: (order[e["category"]], e["name"].casefold(), e["url"]))
    collection["categories"] = [{"id": i, "name": n, "description": d} for i, n, d in CATEGORIES]
    collection["categoryMapping"] = mapping
    collection["statistics"]["categories"] = len(CATEGORIES)
    return collection


if __name__ == "__main__":
    collection = json.loads(pathlib.Path(sys.argv[1]).read_text())
    mapping = json.loads(pathlib.Path(sys.argv[2]).read_text())
    result = apply_categories(collection, mapping)
    pathlib.Path(sys.argv[3]).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["statistics"]))
