(() => {
  try {
    const theme = localStorage.getItem("jev-atlas-theme");
    if (["light", "dark", "auto"].includes(theme)) {
      document.documentElement.dataset.theme = theme;
    }
  } catch {
    document.documentElement.dataset.theme = "auto";
  }
  document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("theme-toggle");
    if (!button) return;
    const themes = ["auto", "light", "dark"];
    function update() {
      const current = document.documentElement.dataset.theme || "auto";
      const next = themes[(themes.indexOf(current) + 1) % themes.length];
      const label = `Theme: ${current === "auto" ? "system" : current}. Switch to ${next === "auto" ? "system" : next} theme`;
      button.setAttribute("aria-label", label);
      button.title = label;
      button.textContent =
        current === "dark" ? "☾" : current === "light" ? "☀" : "◐";
    }
    button.addEventListener("click", () => {
      const current = document.documentElement.dataset.theme || "auto";
      const next = themes[(themes.indexOf(current) + 1) % themes.length];
      document.documentElement.dataset.theme = next;
      try {
        localStorage.setItem("jev-atlas-theme", next);
      } catch {
        /* Apply the theme for this session. */
      }
      update();
    });
    update();
  });
})();
