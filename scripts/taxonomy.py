"""Navigation taxonomy: broad categories with focused, exclusive subcategories."""

SUBCATEGORIES = {
    "start": [
        (
            "overview",
            "Product & introductions",
            "Product overview, launch introductions and first-party homepages.",
        ),
        (
            "quickstarts",
            "Quick starts",
            "First request, installation, beginner setup and getting started.",
        ),
        (
            "api",
            "API & reference",
            "HTTP contracts, API reference, SDK reference and model limits.",
        ),
        (
            "primitives",
            "Primitives & concepts",
            "Choice, Score, Noul, state, confidence and conceptual documentation.",
        ),
        (
            "console",
            "Console & official tools",
            "Official console, demos, playgrounds and first-party developer tools.",
        ),
    ],
    "sdks": [
        ("python", "Python clients", "Python language API clients and SDK libraries."),
        (
            "javascript",
            "JavaScript & TypeScript",
            "JavaScript, TypeScript, Node and browser SDK libraries.",
        ),
        ("go", "Go clients", "Go language API clients and SDKs."),
        ("rust", "Rust clients", "Rust language API clients and SDKs."),
        ("dotnet", ".NET clients", "C#, F# and .NET API clients."),
        ("apple", "Swift & Apple platforms", "Swift, Objective-C and Apple platform SDKs."),
        (
            "other-languages",
            "Other languages & clients",
            "Ruby, PHP, Java, Kotlin and other explicit language clients not covered above.",
        ),
    ],
    "integrations": [
        (
            "frameworks",
            "AI frameworks",
            "Adapters in AI and agent frameworks; excludes MCP and plain language clients.",
        ),
        (
            "platforms",
            "Developer platforms",
            "Application platforms, web frameworks and platform integrations.",
        ),
        (
            "automation",
            "Workflow automation",
            "Automation platforms, workflows, n8n, Zapier and orchestration integrations.",
        ),
        ("databases", "Databases & backends", "Database, backend and data-service integrations."),
    ],
    "access": [
        (
            "gateways",
            "API gateways & proxies",
            "Model gateways, routing proxies, OpenRouter and Vercel Gateway access.",
        ),
        (
            "cloud",
            "Cloud platforms",
            "Cloud provider hosted models and cloud deployment platforms.",
        ),
        (
            "serving",
            "Hosting & serving",
            "Model access, deployment and serving tools not primarily a gateway.",
        ),
    ],
    "observability": [
        (
            "tracing",
            "Tracing & debugging",
            "Trace viewers, request logs, observability integrations and debugging.",
        ),
        (
            "cost",
            "Cost & usage tracking",
            "Token usage, API cost monitoring, budgets and usage metrics.",
        ),
        (
            "operations",
            "Runtime operations",
            "Infrastructure monitoring, health, reliability and operational tooling.",
        ),
    ],
    "agents": [
        (
            "routing",
            "Model & task routing",
            "Routes models, tasks, skills or requests in general agent systems.",
        ),
        (
            "memory",
            "Memory & context",
            "Memory retrieval, compaction, context pruning and retention.",
        ),
        (
            "harnesses",
            "Harnesses & orchestration",
            "Agent execution harnesses, multi-agent coordinators and framework runtimes.",
        ),
        (
            "tools",
            "Tool selection & execution",
            "Tool selection, tool management and agent action planning.",
        ),
        (
            "assistants",
            "Autonomous assistants",
            "General-purpose agents, bots and autonomous assistants with specific implementations.",
        ),
    ],
    "skills": [
        ("mcp", "MCP servers", "MCP servers and MCP tool collections."),
        ("packs", "Skill collections", "Skill packs and reusable agent skill instructions."),
        ("plugins", "Agent plugins", "Plugins and extensions for established agent systems."),
        (
            "selection",
            "Skill discovery & routing",
            "Selecting, discovering and routing agent skills.",
        ),
    ],
    "coding": [
        (
            "review",
            "Code review & verification",
            "Code reviews, diff judgment, pull-request review and code verification.",
        ),
        (
            "agents",
            "Coding agents",
            "Coding agent implementations, coding assistants and development harnesses.",
        ),
        (
            "search",
            "Semantic code search",
            "Code search, semantic grep, code indexing and repository understanding.",
        ),
        (
            "terminal",
            "Terminal & CLI tools",
            "Shell tools, command line interfaces and terminal developer workflows.",
        ),
        (
            "git-ci",
            "Git, CI & testing",
            "Git workflows, CI pipelines, release validation, testing and build tools.",
        ),
        (
            "routing",
            "Coding model routers",
            "Routing models and reasoning effort specifically for coding agents.",
        ),
        (
            "context",
            "Coding context & memory",
            "Context compaction, pruning, memory and skill management specifically for coding agents.",
        ),
    ],
    "browser": [
        (
            "web",
            "Web browser agents",
            "Agents that interact with websites and select browser actions.",
        ),
        (
            "desktop",
            "Desktop & computer use",
            "Desktop GUI control, screenshots, OCR and operating-system interaction.",
        ),
        ("mobile", "Mobile automation", "Android, iOS, phone apps and mobile device interaction."),
        (
            "tooling",
            "Browser infrastructure",
            "Browser libraries, testing platforms, browser servers and browser execution tooling.",
        ),
    ],
    "robotics": [
        ("drones", "Drones & flight", "Drone control, flight and aerial navigation."),
        (
            "embodied",
            "Embodied robots",
            "Physical robots, embodied control and robotic manipulation.",
        ),
        (
            "simulation",
            "Simulation environments",
            "MuJoCo, physics simulation, simulated robots and robotics environments.",
        ),
    ],
    "search": [
        (
            "rag",
            "RAG & document retrieval",
            "Retrieval augmented generation and finding relevant documents.",
        ),
        (
            "reranking",
            "Ranking & reranking",
            "Search result ranking and candidate relevance scoring.",
        ),
        (
            "semantic",
            "Semantic search",
            "Semantic search, matching and indexing of general content.",
        ),
        ("web", "Web research", "Web searching, research assistants and information discovery."),
        (
            "knowledge",
            "Knowledge graphs",
            "Entity alignment, knowledge graph search and structured knowledge retrieval.",
        ),
    ],
    "safety": [
        (
            "injection",
            "Prompt injection & security",
            "Injection detection, malicious content, vulnerability detection and security defenses.",
        ),
        (
            "moderation",
            "Content moderation",
            "Abuse detection, spam, harmful content and community moderation.",
        ),
        (
            "gating",
            "Tool & action gates",
            "Permissions and approval of tool calls, commands and agent actions.",
        ),
        (
            "verification",
            "Output & claim verification",
            "Checks claims, citations, answers, artifacts and completion evidence.",
        ),
        (
            "policy",
            "Policy & compliance",
            "Policy enforcement, compliance rules and other safety constraints.",
        ),
    ],
    "data": [
        (
            "classification",
            "Classification & labeling",
            "Classifies records, assigns labels, creates labeled datasets and categorizes data.",
        ),
        (
            "extraction",
            "Structured extraction",
            "Extracts fields, values and structured records from text or documents.",
        ),
        (
            "sql",
            "SQL & databases",
            "Data processing using SQL or database queries and database decision integrations.",
        ),
        (
            "pipelines",
            "Data pipelines & quality",
            "Batch processing, ETL, data transformations and quality checks.",
        ),
    ],
    "benchmarks": [
        (
            "accuracy",
            "Accuracy & comparisons",
            "Model accuracy comparisons, benchmark performance and independent measurements.",
        ),
        (
            "speed-cost",
            "Latency & cost",
            "Measures latency, speed, costs, throughput and runtime performance.",
        ),
        (
            "calibration",
            "Calibration & consistency",
            "Probability calibration, consistency, repeatability and uncertainty measurements.",
        ),
        (
            "security",
            "Security evaluations",
            "Benchmarks prompt injection defenses, vulnerabilities and security properties.",
        ),
        (
            "harnesses",
            "Evaluation harnesses",
            "Software for running evaluations, tests and benchmark suites.",
        ),
        (
            "datasets",
            "Datasets & case studies",
            "Evaluation datasets, measured case studies and benchmark reports not in other specific groups.",
        ),
    ],
    "models": [
        (
            "replicas",
            "Open implementations",
            "Open System One replicas, reimplementations and alternative model projects.",
        ),
        (
            "training",
            "Training & distillation",
            "Model training, RLCD, fine-tuning, learning algorithms and distillation.",
        ),
        (
            "servers",
            "Compatible servers",
            "Inference servers and servers implementing a compatible decision API.",
        ),
        (
            "adapters",
            "Compatibility adapters",
            "Adapters that translate decisions to other model providers and existing APIs.",
        ),
    ],
    "games": [
        (
            "arcade",
            "Arcade & classic games",
            "Tetris, Mario, Pac-Man, Doom and similar arcade or classic game agents.",
        ),
        (
            "strategy",
            "Strategy & puzzles",
            "Chess, strategy, puzzles, board games, logic games and planning games.",
        ),
        (
            "worlds",
            "Interactive worlds",
            "Interactive simulated worlds, characters, social simulations and role-playing.",
        ),
        (
            "playful",
            "Playful experiments",
            "Other playful demos, toys and fun interactive experiences.",
        ),
    ],
    "finance": [
        (
            "trading",
            "Trading agents",
            "Agents placing or deciding trades, including cryptocurrency trading.",
        ),
        (
            "signals",
            "Signals & market analysis",
            "Market analysis, market signals, research and asset scoring.",
        ),
        (
            "risk",
            "Risk & financial workflows",
            "Financial risk, fraud, financial document processing and financial workflow automation.",
        ),
    ],
    "apps": [
        ("email", "Email & inboxes", "Email sorting, inbox automation and email helpers."),
        ("notes", "Notes & knowledge", "Notes, personal knowledge, documents and reading helpers."),
        (
            "planning",
            "Calendars & planning",
            "Calendar, scheduling, planning and personal task management.",
        ),
        (
            "utilities",
            "Everyday utilities",
            "Personal utilities, general apps, notifications and lifestyle tools.",
        ),
        (
            "workflows",
            "Personal automation",
            "Automation of everyday personal and professional workflows.",
        ),
    ],
    "commerce": [
        (
            "shopping",
            "Shopping & recommendations",
            "Shopping, product matching, e-commerce and product recommendations.",
        ),
        (
            "marketing",
            "Marketing & advertising",
            "Marketing content, advertising, growth and campaign decisions.",
        ),
        (
            "business",
            "Business operations",
            "Other commerce operations, websites and commercial workflow applications.",
        ),
    ],
    "support": [
        (
            "tickets",
            "Ticket routing & triage",
            "Support ticket classification, routing and triage.",
        ),
        (
            "service",
            "Customer service",
            "Customer communication, support assistants and resolution workflows.",
        ),
        (
            "sales",
            "Sales & lead qualification",
            "Sales assistance, lead scoring and sales quality checks.",
        ),
    ],
    "science": [
        (
            "legal",
            "Legal & contracts",
            "Law, contracts, compliance and legal document applications.",
        ),
        (
            "health",
            "Health & medicine",
            "Healthcare, clinical, medical and wellbeing applications.",
        ),
        (
            "research",
            "Scientific applications",
            "Scientific analysis, experiments and research in other professional domains.",
        ),
    ],
    "creative": [
        (
            "writing",
            "Writing & publishing",
            "Writing, editing, publishing, text and creative storytelling.",
        ),
        (
            "visual",
            "Visual media & design",
            "Images, video, visual design and visual artifact quality.",
        ),
        ("audio", "Music & audio creation", "Music, creative audio and sound design."),
    ],
    "voice": [
        (
            "assistants",
            "Voice assistants",
            "Voice and conversational agents and speech-driven assistants.",
        ),
        (
            "speech",
            "Speech processing",
            "Transcription, speech analysis and voice data processing.",
        ),
        (
            "realtime",
            "Real-time communication",
            "Live communication, calls, real-time interaction and conversation routing.",
        ),
    ],
    "education": [
        ("tutors", "Tutors & learning apps", "Learner-facing tutors and educational applications."),
        (
            "assessment",
            "Assessment & grading",
            "Grading, assessment, student feedback and educational evaluation.",
        ),
        (
            "teaching",
            "Teaching resources",
            "Teaching workflows and educational resources for instructors.",
        ),
    ],
    "demos": [
        (
            "playgrounds",
            "API playgrounds",
            "Interactive API playgrounds, sandboxes and request explorers.",
        ),
        (
            "examples",
            "Runnable examples",
            "General-purpose runnable examples and demonstration projects.",
        ),
        (
            "prototypes",
            "Experimental prototypes",
            "Technical prototypes and experiments without a more specific application domain.",
        ),
    ],
    "patterns": [
        (
            "routing",
            "Routing & selection",
            "Routing, action selection, intent dispatch and speculative fan-out patterns.",
        ),
        (
            "scoring",
            "Scoring & ranking",
            "Composite scoring, rankings and rubric-based scoring patterns.",
        ),
        (
            "verification",
            "Verification & gates",
            "Verification, evidence checking and confidence gates as architectural recipes.",
        ),
        (
            "confidence",
            "Confidence & uncertainty",
            "Thresholds, calibrated probabilities and handling uncertainty in architecture.",
        ),
    ],
    "learning": [
        (
            "guides",
            "Guides & tutorials",
            "How-to guides, tutorials, cookbooks, cheat sheets and developer learning articles.",
        ),
        ("talks", "Talks & videos", "Recorded talks, videos, presentations and podcasts."),
        (
            "news",
            "News & announcements",
            "Product news, launch coverage, announcements and community updates.",
        ),
        (
            "analysis",
            "Analysis & discussions",
            "Long-form analysis, critiques, discussions, threads and technical research essays.",
        ),
        (
            "cases",
            "Examples & case studies",
            "Learning from application examples and narrative case studies without measured benchmarks.",
        ),
    ],
    "community": [
        (
            "directories",
            "Directories & collections",
            "Curated lists, directories, catalogs, broader resource collections and awesome lists.",
        ),
        (
            "channels",
            "Communities & channels",
            "Community groups, chat servers, forums and community channels.",
        ),
        (
            "people",
            "Builders & accounts",
            "Builder profiles, community people and social media accounts.",
        ),
    ],
    "other": [
        (
            "experiments",
            "Other experiments",
            "Experiments and application ideas whose domain is not covered by another parent category.",
        ),
        (
            "references",
            "Additional references",
            "Supporting documents, code files and reference pages without a more specific grouping.",
        ),
    ],
}


def catalog(parent):
    items = SUBCATEGORIES[parent]
    return [
        {"id": parent + "-" + slug, "description": name + ". " + description}
        for slug, name, description in items
    ] + [
        {
            "id": parent + "-general",
            "description": "General resources. Use only when the supplied name and description do not justify any more specific subcategory. A safe broad fallback.",
        }
    ]


def all_subcategories():
    definitions = [
        {"id": parent + "-" + slug, "parent": parent, "name": name, "description": description}
        for parent, items in SUBCATEGORIES.items()
        for slug, name, description in items
        + [
            (
                "projects",
                "More projects & source code",
                "Additional projects and source files with insufficient evidence for a narrower topic.",
            ),
            (
                "posts",
                "More posts & discussions",
                "Additional social posts and forum discussions in this category.",
            ),
            (
                "videos",
                "More videos & channels",
                "Additional videos and video channels in this category.",
            ),
            (
                "packages",
                "More packages & releases",
                "Additional package registry pages and software releases in this category.",
            ),
            (
                "references",
                "More guides & websites",
                "Additional reference pages and websites in this category.",
            ),
        ]
    ]
    unique = {}
    for definition in definitions:
        unique.setdefault(definition["id"], definition)
    return list(unique.values())
