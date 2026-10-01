(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const pageSize = 48;
  const controls = {
    search: $("search"),
    category: $("category-filter"),
    subcategory: $("subcategory-filter"),
    sort: $("sort"),
    saved: $("saved-filter"),
    view: $("view-toggle"),
  };
  let catalog;
  let entries = [];
  let visible = pageSize;
  let savedOnly = false;
  let cardView = false;
  let saved = new Set();
  let pendingFrame;
  function readPreference(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key)) ?? fallback;
    } catch {
      return fallback;
    }
  }
  function writePreference(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* Browsing works when storage is unavailable. */
    }
  }
  const savedPreference = readPreference("jev-atlas-saved", []);
  saved = new Set(
    Array.isArray(savedPreference)
      ? savedPreference.filter((x) => typeof x === "string")
      : [],
  );
  cardView = readPreference("jev-atlas-cards", false) === true;
  function closeMenu() {
    $("category-nav").classList.remove("open");
    $("menu-toggle").setAttribute("aria-expanded", "false");
    $("menu-toggle").setAttribute("aria-label", "Open category menu");
  }
  $("menu-toggle").addEventListener("click", () => {
    const open = $("category-nav").classList.toggle("open");
    $("menu-toggle").setAttribute("aria-expanded", String(open));
    $("menu-toggle").setAttribute(
      "aria-label",
      open ? "Close category menu" : "Open category menu",
    );
    if (open) $("category-nav").querySelector("a").focus();
  });
  document.addEventListener("click", (event) => {
    if (
      !$("category-nav").contains(event.target) &&
      !$("menu-toggle").contains(event.target)
    )
      closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    const isTyping =
      event.target instanceof HTMLElement &&
      (event.target.isContentEditable ||
        /INPUT|TEXTAREA|SELECT/.test(event.target.tagName));
    if (
      event.key === "/" &&
      !isTyping &&
      !event.ctrlKey &&
      !event.metaKey &&
      !event.altKey
    ) {
      event.preventDefault();
      controls.search.focus();
    }
    if (
      event.key === "Escape" &&
      $("category-nav").classList.contains("open")
    ) {
      closeMenu();
      $("menu-toggle").focus();
    }
  });

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function card(entry) {
    const article = element("article", "resource-card");
    article.dataset.entry = entry.id;
    const top = element("div", "card-topline");
    const icon = element(
      "span",
      "resource-icon",
      entry.name.slice(0, 2).toUpperCase(),
    );
    icon.setAttribute("aria-hidden", "true");
    top.append(
      icon,
      element(
        "span",
        "resource-domain",
        new URL(entry.url).hostname.replace(/^www\./, ""),
      ),
    );
    const save = element(
      "button",
      "save-button",
      saved.has(entry.id) ? "♥" : "♡",
    );
    save.type = "button";
    save.dataset.save = entry.id;
    save.setAttribute("aria-pressed", String(saved.has(entry.id)));
    save.setAttribute(
      "aria-label",
      `${saved.has(entry.id) ? "Unsave" : "Save"} ${entry.name}`,
    );
    top.append(save);
    const heading = element("h3");
    const link = element("a", "", entry.name);
    link.href = entry.url;
    const arrow = element("span", "external-arrow", "↗");
    arrow.setAttribute("aria-hidden", "true");
    link.append(arrow);
    heading.append(link);
    const description = element("p", "resource-description", entry.description);
    const category = element(
      "a",
      "category-tag",
      catalog.categories.find((c) => c.id === entry.category).name,
    );
    category.href = `?category=${encodeURIComponent(entry.category)}#results`;
    category.dataset.category = entry.category;
    const star = element("span", "card-stars", "★ " + starText(entry));
    star.title =
      "Containing repository stars from an imported snapshot; not live";
    top.append(star);
    category.textContent +=
      " / " +
      catalog.subcategories.find((sub) => sub.id === entry.subcategory).name;
    category.dataset.subcategory = entry.subcategory;
    article.append(top, heading, description, category);
    return article;
  }
  function starText(entry) {
    return entry.stars === null
      ? "—"
      : (entry.starsApproximate ? "≈" : "") + entry.stars.toLocaleString();
  }
  function table(items) {
    const table = element("table", "resource-table");
    const caption = element(
      "caption",
      "sr-only",
      "Resources, repository stars, descriptions and categories",
    );
    table.append(caption);
    const head = element("thead");
    const header = element("tr");
    for (const label of [
      "Resource",
      "Stars",
      "Description",
      "Category",
      "Save",
    ]) {
      const th = element("th", "", label);
      th.scope = "col";
      if (label === "Save") {
        th.textContent = "";
        th.append(element("span", "sr-only", "Save"));
      }
      header.append(th);
    }
    head.append(header);
    table.append(head);
    const body = element("tbody");
    for (const entry of items) {
      const row = element("tr", "resource-item");
      row.dataset.entry = entry.id;
      const name = element("td", "resource-name");
      const link = element("a", "resource-link", entry.name);
      link.href = entry.url;
      name.append(
        link,
        element(
          "span",
          "resource-host",
          new URL(entry.url).hostname.replace(/^www\./, ""),
        ),
      );
      const stars = element("td", "stars-cell", starText(entry));
      stars.dataset.label = "Stars";
      stars.title = `Repository stars imported ${entry.starsAsOf || "without a count"}; not live`;
      const description = element("td", "description-cell", entry.description);
      const category = element("td", "category-cell");
      const tag = element(
        "a",
        "",
        catalog.categories.find((c) => c.id === entry.category).name,
      );
      tag.href = `?category=${entry.category}&subcategory=${entry.subcategory}#results`;
      tag.dataset.category = entry.category;
      tag.dataset.subcategory = entry.subcategory;
      category.append(
        tag,
        element(
          "small",
          "",
          catalog.subcategories.find((sub) => sub.id === entry.subcategory)
            .name,
        ),
      );
      const saveCell = element("td", "save-cell");
      const save = element(
        "button",
        "save-button",
        saved.has(entry.id) ? "♥" : "♡",
      );
      save.type = "button";
      save.dataset.save = entry.id;
      save.setAttribute("aria-pressed", String(saved.has(entry.id)));
      save.setAttribute(
        "aria-label",
        `${saved.has(entry.id) ? "Unsave" : "Save"} ${entry.name}`,
      );
      saveCell.append(save);
      row.append(name, stars, description, category, saveCell);
      body.append(row);
    }
    table.append(body);
    return table;
  }
  function subcategoryOptions(selected = "all") {
    controls.subcategory.replaceChildren(
      new Option("All subcategories", "all"),
    );
    for (const sub of catalog.subcategories) {
      if (
        controls.category.value === "all" ||
        sub.parent === controls.category.value
      )
        controls.subcategory.add(new Option(sub.name, sub.id));
    }
    controls.subcategory.value = [...controls.subcategory.options].some(
      (option) => option.value === selected,
    )
      ? selected
      : "all";
  }
  function parseUrl() {
    const params = new URLSearchParams(location.search);
    controls.search.value = params.get("q") || "";
    const category =
      params.get("category") || document.body.dataset.defaultCategory || "all";
    controls.category.value = catalog.categories.some((c) => c.id === category)
      ? category
      : "all";
    const sub = catalog.subcategories.find(
      (sub) => sub.id === params.get("subcategory"),
    );
    if (sub) controls.category.value = sub.parent;
    subcategoryOptions(sub ? sub.id : "all");
    controls.sort.value = ["stars", "category", "name"].includes(
      params.get("sort"),
    )
      ? params.get("sort")
      : "stars";
    savedOnly = params.get("saved") === "1";
  }
  function updateUrl() {
    const params = new URLSearchParams();
    const query = controls.search.value.trim();
    if (query) params.set("q", query);
    if (controls.category.value !== "all")
      params.set("category", controls.category.value);
    else if (document.body.dataset.defaultCategory !== "all")
      params.set("category", "all");
    if (controls.subcategory.value !== "all")
      params.set("subcategory", controls.subcategory.value);
    if (controls.sort.value !== "stars")
      params.set("sort", controls.sort.value);
    if (savedOnly) params.set("saved", "1");
    const queryString = params.toString();
    history.replaceState(
      null,
      "",
      location.pathname +
        (queryString ? "?" + queryString : "") +
        location.hash,
    );
  }
  function render(updateLocation = true) {
    if (!catalog) return;
    const words = controls.search.value
      .trim()
      .toLocaleLowerCase()
      .split(/\s+/)
      .filter(Boolean);
    const filtered = entries.filter(
      (entry) =>
        words.every((word) => entry.searchText.includes(word)) &&
        (controls.category.value === "all" ||
          entry.category === controls.category.value) &&
        (controls.subcategory.value === "all" ||
          entry.subcategory === controls.subcategory.value) &&
        (!savedOnly || saved.has(entry.id)),
    );
    if (controls.sort.value === "category")
      filtered.sort(
        (a, b) =>
          catalog.categories.findIndex((c) => c.id === a.category) -
            catalog.categories.findIndex((c) => c.id === b.category) ||
          a.name.localeCompare(b.name),
      );
    if (controls.sort.value === "stars")
      filtered.sort(
        (a, b) =>
          (b.stars ?? -1) - (a.stars ?? -1) || a.name.localeCompare(b.name),
      );
    const shown = filtered.slice(0, visible);
    if (cardView) {
      const grid = element("div", "resource-grid");
      for (const entry of shown) grid.append(card(entry));
      $("results").replaceChildren(grid);
    } else $("results").replaceChildren(table(shown));
    const parentName =
      controls.category.value === "all"
        ? "All resources"
        : catalog.categories.find((c) => c.id === controls.category.value).name;
    const subName =
      controls.subcategory.value === "all"
        ? ""
        : " / " +
          catalog.subcategories.find(
            (sub) => sub.id === controls.subcategory.value,
          ).name;
    $("breadcrumb").textContent = parentName + subName;
    $("result-count").textContent =
      `${filtered.length.toLocaleString()} of ${entries.length.toLocaleString()} resources${controls.category.value === "all" ? "" : " · " + catalog.categories.find((c) => c.id === controls.category.value).name}`;
    $("page-status").textContent =
      `Showing ${shown.length.toLocaleString()} of ${filtered.length.toLocaleString()} matching resources`;
    $("load-more").hidden = shown.length >= filtered.length;
    $("load-more").textContent =
      `Load ${Math.min(pageSize, filtered.length - shown.length)} more resources`;
    $("empty-state").hidden = filtered.length !== 0;
    controls.saved.setAttribute("aria-pressed", String(savedOnly));
    $("saved-count").textContent = String(saved.size);
    controls.view.setAttribute("aria-pressed", String(cardView));
    controls.view.setAttribute(
      "aria-label",
      cardView ? "Switch to table view" : "Switch to card view",
    );
    controls.view.title = controls.view.getAttribute("aria-label");
    for (const link of document.querySelectorAll(
      ".category-link, .subcategory-link",
    )) {
      if (
        link.dataset.category === controls.category.value &&
        (link.dataset.subcategory || "all") === controls.subcategory.value
      )
        link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    }
    for (const group of document.querySelectorAll(".nav-group"))
      if (group.dataset.parent === controls.category.value) group.open = true;
    if (updateLocation) updateUrl();
  }
  function reset() {
    controls.search.value = "";
    controls.category.value = "all";
    controls.sort.value = "stars";
    subcategoryOptions();
    savedOnly = false;
    visible = pageSize;
    render();
  }
  function scheduleRender() {
    visible = pageSize;
    cancelAnimationFrame(pendingFrame);
    pendingFrame = requestAnimationFrame(() => render());
  }
  controls.search.addEventListener("input", scheduleRender);
  controls.category.addEventListener("change", () => {
    if (catalog) subcategoryOptions();
    scheduleRender();
  });
  controls.subcategory.addEventListener("change", () => {
    if (catalog && controls.subcategory.value !== "all") {
      const sub = catalog.subcategories.find(
        (sub) => sub.id === controls.subcategory.value,
      );
      controls.category.value = sub.parent;
      subcategoryOptions(sub.id);
    }
    scheduleRender();
  });
  controls.sort.addEventListener("change", scheduleRender);
  $("filters").addEventListener("submit", (event) => event.preventDefault());
  controls.saved.addEventListener("click", () => {
    savedOnly = !savedOnly;
    visible = pageSize;
    render();
  });
  controls.view.addEventListener("click", () => {
    cardView = !cardView;
    writePreference("jev-atlas-cards", cardView);
    render(false);
  });
  $("clear-filters").addEventListener("click", reset);
  $("empty-reset").addEventListener("click", reset);
  $("load-more").addEventListener("click", () => {
    const previous = visible;
    visible += pageSize;
    render(false);
    const next = $("results").querySelectorAll("[data-entry]")[previous];
    if (next) next.querySelector("a").focus({ preventScroll: true });
  });
  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const category = event.target.closest("[data-category]");
    if (
      category &&
      catalog &&
      !event.ctrlKey &&
      !event.metaKey &&
      !event.shiftKey &&
      !event.altKey
    ) {
      event.preventDefault();
      controls.category.value = category.dataset.category;
      subcategoryOptions(category.dataset.subcategory || "all");
      visible = pageSize;
      render();
      closeMenu();
      $("results").focus({ preventScroll: true });
      $("results").scrollIntoView({ block: "start" });
    }
    const save = event.target.closest("[data-save]");
    if (save && catalog) {
      const id = save.dataset.save;
      if (saved.has(id)) saved.delete(id);
      else saved.add(id);
      writePreference("jev-atlas-saved", [...saved]);
      if (savedOnly) render(false);
      else {
        const entry = entries.find((e) => e.id === id);
        save.textContent = saved.has(id) ? "♥" : "♡";
        save.setAttribute("aria-pressed", String(saved.has(id)));
        save.setAttribute(
          "aria-label",
          `${saved.has(id) ? "Unsave" : "Save"} ${entry.name}`,
        );
        $("saved-count").textContent = String(saved.size);
      }
    }
  });
  addEventListener("popstate", () => {
    if (catalog) {
      parseUrl();
      visible = pageSize;
      render(false);
    }
  });
  addEventListener("storage", (event) => {
    if (event.key === "jev-atlas-saved") {
      const value = readPreference("jev-atlas-saved", []);
      saved = new Set(Array.isArray(value) ? value : []);
      render(false);
    }
  });
  fetch(document.body.dataset.catalog)
    .then((response) => {
      if (!response.ok)
        throw new Error(`Catalog request failed (${response.status})`);
      return response.json();
    })
    .then((data) => {
      catalog = data;
      entries = data.entries.map((entry) => ({
        ...entry,
        searchText: (entry.name + " " + entry.description).toLocaleLowerCase(),
      }));
      entries.sort(
        (a, b) =>
          a.name.localeCompare(b.name, "en", { sensitivity: "base" }) ||
          a.url.localeCompare(b.url),
      );
      saved = new Set(
        [...saved].filter((id) => entries.some((entry) => entry.id === id)),
      );
      parseUrl();
      visible = pageSize;
      render(false);
      document.body.dataset.ready = "true";
    })
    .catch(() => {
      $("app-error").hidden = false;
      $("app-error").textContent =
        "Live search could not load. You can still browse the complete static category pages using the category menu. Reload this page to retry.";
    });
})();
