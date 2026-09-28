const form = document.getElementById("comic-form");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const exportBtn = document.getElementById("export-btn");

if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    data.num_panels = parseInt(data.num_panels || "4", 10);

    statusEl.textContent = "Drawing your comic... this can take a minute.";
    document.getElementById("generate-btn").disabled = true;

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Generation failed");

      statusEl.textContent = "";
      document.getElementById("comic-title").textContent = json.title;
      const grid = document.getElementById("panel-grid");
      grid.innerHTML = "";
      for (const p of json.panels) {
        grid.insertAdjacentHTML(
          "beforeend",
          `<article class="panel ${p.span_class}">
             ${p.image_path ? `<img src="/static/${p.image_path}" alt="${p.title}" />` : ""}
             <h3>Panel ${p.index}: ${p.title}</h3>
             <p>${p.caption}</p>
           </article>`
        );
      }
      resultEl.classList.remove("hidden");
      resultEl.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      statusEl.textContent = "Error: " + err.message;
    } finally {
      document.getElementById("generate-btn").disabled = false;
    }
  });
}

if (exportBtn) {
  exportBtn.addEventListener("click", async () => {
    statusEl.textContent = "Building PDF...";
    try {
      const res = await fetch("/api/export", { method: "POST" });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Export failed");
      window.location.href = "/export-success?pdf=" + encodeURIComponent(json.pdf_url);
    } catch (err) {
      statusEl.textContent = "Error: " + err.message;
    }
  });
}
