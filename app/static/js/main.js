window.addEventListener("load", () => {
  document.getElementById("loader")?.classList.add("hidden");
});

document.querySelector("[data-menu-toggle]")?.addEventListener("click", () => {
  document.querySelector("[data-menu]")?.classList.toggle("open");
});

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.classList.add("visible");
  });
}, { threshold: 0.15 });
document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));

document.querySelectorAll(".counter").forEach((counter) => {
  const target = Number(counter.dataset.count || 0);
  let current = 0;
  const step = Math.max(1, Math.ceil(target / 70));
  const tick = () => {
    current += step;
    counter.textContent = current >= target ? target : current;
    if (current < target) requestAnimationFrame(tick);
  };
  tick();
});

const financeCanvas = document.getElementById("financeChart");
if (financeCanvas && window.Chart) {
  const rows = JSON.parse(financeCanvas.dataset.finance || "[]");
  new Chart(financeCanvas, {
    type: "bar",
    data: {
      labels: rows.map((row) => row.month),
      datasets: [
        { type: "bar", label: "Revenue", data: rows.map((row) => row.revenue), borderColor: "#b76e79", backgroundColor: "rgba(183,110,121,.42)", borderRadius: 12 },
        { type: "bar", label: "Expense", data: rows.map((row) => row.expense), borderColor: "#8aa399", backgroundColor: "rgba(138,163,153,.34)", borderRadius: 12 },
        { type: "line", label: "Profit", data: rows.map((row) => row.profit), borderColor: "#d4a373", backgroundColor: "rgba(212,163,115,.16)", tension: .38, fill: true, pointRadius: 4, pointHoverRadius: 6 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { boxWidth: 12, usePointStyle: true } },
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: Rs. ${Number(context.raw || 0).toLocaleString("en-IN")}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: (value) => `Rs. ${Number(value).toLocaleString("en-IN")}` },
          grid: { color: "rgba(48,39,43,.08)" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

const categoryCanvas = document.getElementById("categoryChart");
if (categoryCanvas && window.Chart) {
  const rows = JSON.parse(categoryCanvas.dataset.categories || "[]");
  new Chart(categoryCanvas, {
    type: "doughnut",
    data: {
      labels: rows.map((row) => row.category),
      datasets: [{ data: rows.map((row) => row.count), backgroundColor: ["#e9b4c8", "#c9b6e4", "#f1d2a9", "#a7c7b7", "#f3a6a1", "#b7d7e8"] }]
    },
    options: { responsive: true, maintainAspectRatio: false, cutout: "58%", plugins: { legend: { position: "bottom" } } }
  });
}

const materialRows = Array.from(document.querySelectorAll(".material-row-dynamic"));
const addMaterialButton = document.querySelector("[data-add-material]");
const materialLimitNote = document.querySelector("[data-material-limit-note]");
const materialTotal = document.querySelector("[data-material-total]");

if (materialRows.length && addMaterialButton) {
  const rowHasValue = (row) => Array.from(row.querySelectorAll("input")).some((input) => input.value.trim() !== "");
  const showRow = (row) => {
    row.hidden = false;
    row.querySelectorAll("input").forEach((input) => {
      input.disabled = false;
    });
  };
  const hideRow = (row) => {
    row.hidden = true;
    row.querySelectorAll("input").forEach((input) => {
      input.disabled = true;
    });
  };
  const updateNote = () => {
    const visibleCount = materialRows.filter((row) => !row.hidden).length;
    if (materialLimitNote) materialLimitNote.textContent = `${visibleCount} of ${materialRows.length} material rows shown.`;
    if (visibleCount >= materialRows.length) {
      addMaterialButton.disabled = true;
      addMaterialButton.textContent = "Maximum 40 rows reached";
    }
  };
  const updateMaterialTotal = () => {
    if (!materialTotal) return;
    const total = materialRows.reduce((sum, row) => {
      if (row.hidden) return sum;
      const amountInput = row.querySelector("input[id$='-amount']");
      const amount = Number.parseFloat(amountInput?.value || "0");
      return sum + (Number.isFinite(amount) ? amount : 0);
    }, 0);
    materialTotal.textContent = `Rs. ${total.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
  };

  materialRows.forEach((row, index) => {
    if (index === 0 || rowHasValue(row)) showRow(row);
    else hideRow(row);
    row.querySelectorAll("input").forEach((input) => {
      input.addEventListener("input", updateMaterialTotal);
    });
  });
  updateNote();
  updateMaterialTotal();

  addMaterialButton.addEventListener("click", () => {
    const nextRow = materialRows.find((row) => row.hidden);
    if (nextRow) {
      showRow(nextRow);
      nextRow.querySelector("input")?.focus();
    }
    updateNote();
    updateMaterialTotal();
  });
}
