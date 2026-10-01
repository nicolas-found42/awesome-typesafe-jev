# Maintaining the directory

Edit only `data/entries.json` for catalog changes. Each resource has a stable identity, original URL, description, primary category, subcategory and optional repository-star snapshot. Category and subcategory definitions live in this same file. Generated files must not be edited by hand.

Run `uv sync --locked`, `npm ci` and `uv run python scripts/build.py`. Preview the result with `uv run python -m http.server 8000 --directory dist`, then open `http://localhost:8000`.

Validate with `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, `uv run pytest`, `npm run check:js`, `npm run format:check`, `npm test` and `actionlint`.

The browser uses only static JSON, HTML, CSS and JavaScript. It needs no server application, database, AI API or credentials. Saved items and display preferences use browser storage, with a session fallback when storage is blocked.

The import utilities in `scripts/` support pinned intake, deterministic URL merging, semantic category organization and snapshot star enrichment. Keep detailed intake records in the ignored `.local/` directory. Publish only the standalone catalog fields. A refresh must preserve every existing entry unless its removal is explicitly requested.

Repository star counts are cached metadata. Record the import date, preserve the distinction between an exact and rounded count, and use `null` when unavailable. A GitHub source-file entry inherits its containing repository's star count.

Every push to `main` runs validation and deploys `dist/` to GitHub Pages. Pull requests run validation without deployment. The workflow uses the pinned Python and Node versions in `.python-version` and `.node-version`.
