import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync } from "node:fs";

const data = JSON.parse(
  readFileSync(new URL("../data/entries.json", import.meta.url), "utf8"),
);
const matches = (query) =>
  data.entries.filter((e) =>
    (e.name + " " + e.description)
      .toLocaleLowerCase()
      .includes(query.toLocaleLowerCase()),
  );

async function ready(page, url = "/") {
  await page.goto(url);
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
}

test("full catalog, alphabetical rows, counts and pagination", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await ready(page);
  await expect(page.locator("#result-count")).toContainText("11,066 of 11,066");
  await expect(page.locator("#results [data-entry]")).toHaveCount(48);
  await page.getByRole("button", { name: "Load 48 more resources" }).click();
  await expect(page.locator("#results [data-entry]")).toHaveCount(96);
  expect(errors).toEqual([]);
});

test("search filters names and descriptions and survives a shared URL", async ({
  page,
}) => {
  await ready(page);
  await page.getByRole("searchbox").fill("Tetris");
  await expect(page.locator("#result-count")).toContainText(
    `${matches("Tetris").length.toLocaleString()} of`,
  );
  await expect(page).toHaveURL(/q=Tetris/);
  await page.reload();
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(page.getByRole("searchbox")).toHaveValue("Tetris");
  await page.getByRole("searchbox").fill("calibrated");
  await expect(page.locator("#result-count")).toContainText(
    `${matches("calibrated").length.toLocaleString()} of`,
  );
});

test("category and subcategory filters retain accurate counts", async ({
  page,
}) => {
  await ready(page);
  await page.locator("#category-filter").selectOption("coding");
  const coding = data.entries.filter((e) => e.category === "coding");
  await expect(page.locator("#result-count")).toContainText(
    `${coding.length.toLocaleString()} of`,
  );
  await page.locator("#subcategory-filter").selectOption("coding-review");
  const review = coding.filter((e) => e.subcategory === "coding-review");
  await expect(page.locator("#result-count")).toContainText(
    `${review.length.toLocaleString()} of`,
  );
  await expect(page.locator("#breadcrumb")).toContainText("Code review");
  await page.reload();
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(page.locator("#subcategory-filter")).toHaveValue(
    "coding-review",
  );
  await page.locator("#category-filter").selectOption("games");
  await expect(page.locator("#subcategory-filter")).toHaveValue("all");
  await page.getByRole("button", { name: "Reset", exact: true }).click();
  await expect(page.locator("#result-count")).toContainText("11,066 of 11,066");
});

test("nested category navigation and mobile menu work", async ({
  page,
  isMobile,
}) => {
  await ready(page);
  if (isMobile)
    await page.getByRole("button", { name: "Open category menu" }).click();
  const group = page.locator('.nav-group[data-parent="coding"]');
  await group.locator("summary").click();
  await group.locator('[data-subcategory="coding-review"]').click();
  await expect(page.locator("#category-filter")).toHaveValue("coding");
  await expect(page.locator("#subcategory-filter")).toHaveValue(
    "coding-review",
  );
  if (isMobile)
    await expect(page.locator("#menu-toggle")).toHaveAttribute(
      "aria-expanded",
      "false",
    );
});

test("star sorting, missing stars and card view", async ({ page }) => {
  await ready(page);
  await page.locator("#sort").selectOption("stars");
  const max = Math.max(...data.entries.map((e) => e.stars ?? -1));
  await expect(page.locator(".stars-cell").first()).toHaveText(
    max.toLocaleString(),
  );
  await page.getByRole("button", { name: "Switch to card view" }).click();
  await expect(page.locator("#results .resource-card")).toHaveCount(48);
  await expect(page.locator(".card-stars").first()).toContainText(
    max.toLocaleString(),
  );
  await page.reload();
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(page.locator("#results .resource-card")).toHaveCount(48);
  await page.getByRole("button", { name: "Switch to table view" }).click();
  await expect(page.locator("#results table")).toHaveCount(1);
});

test("saved resources persist, filter and can be removed", async ({ page }) => {
  await ready(page);
  const row = page.locator("#results [data-entry]").first();
  const id = await row.getAttribute("data-entry");
  await row.locator(".save-button").click();
  await expect(page.locator("#saved-count")).toHaveText("1");
  await page.locator("#saved-filter").click();
  await expect(page.locator("#results [data-entry]")).toHaveCount(1);
  await expect(page.locator("#results [data-entry]")).toHaveAttribute(
    "data-entry",
    id,
  );
  await page.reload();
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(page.locator("#results [data-entry]")).toHaveCount(1);
  await page.locator("#results .save-button").click();
  await expect(page.locator("#empty-state")).toBeVisible();
  await page.getByRole("button", { name: "Reset filters" }).click();
  await expect(page.locator("#result-count")).toContainText("11,066 of 11,066");
});

test("system theme, manual theme and persistence", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await ready(page);
  expect(
    await page
      .locator("body")
      .evaluate((node) => getComputedStyle(node).backgroundColor),
  ).toBe("rgb(16, 18, 27)");
  await page.locator("#theme-toggle").click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await page.locator("#theme-toggle").click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
});

test("empty results, search shortcut and blocked browser storage", async ({
  page,
}) => {
  await page.addInitScript(() =>
    Object.defineProperty(window, "localStorage", {
      get() {
        throw new Error("Storage blocked");
      },
    }),
  );
  await ready(page);
  await page.keyboard.press("/");
  await expect(page.getByRole("searchbox")).toBeFocused();
  await page.getByRole("searchbox").fill("zzzz-no-resource-matches-4793");
  await expect(page.locator("#empty-state")).toBeVisible();
  await page.getByRole("button", { name: "Reset filters" }).click();
  await page.locator("#results .save-button").first().click();
  await expect(page.locator("#saved-count")).toHaveText("1");
});

test("static category pages work without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:9877/categories/coding.html");
  await expect(page.locator("#results [data-entry]")).toHaveCount(
    data.entries.filter((e) => e.category === "coding").length,
  );
  await expect(page.locator("#subcategory-coding-review")).toBeVisible();
  await context.close();
});

test("catalog failure keeps static browsing available", async ({ page }) => {
  await page.route("**/catalog.json", (route) =>
    route.fulfill({ status: 503, body: "Unavailable" }),
  );
  await page.goto("/");
  await expect(page.locator("#app-error")).toBeVisible();
  await expect(page.locator("#results [data-entry]")).toHaveCount(48);
  expect(
    await page.locator("a[href='./categories/coding.html#results']").count(),
  ).toBeGreaterThan(0);
});

test("responsive layout and standalone presentation", async ({ page }) => {
  await ready(page);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await expect(page.locator("#source-filter, .source-details")).toHaveCount(0);
  await expect(page.locator(".site-header")).not.toContainText("Sources");
  await page.screenshot({
    path: `test-results/preview-${test.info().project.name}.png`,
  });
});

test("accessibility in light and dark themes", async ({ page }) => {
  await ready(page);
  for (const theme of ["light", "dark"]) {
    await page.locator("html").evaluate((node, value) => {
      node.dataset.theme = value;
    }, theme);
    const result = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(result.violations).toEqual([]);
  }
});
