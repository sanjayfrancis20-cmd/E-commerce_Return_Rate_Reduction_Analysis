/**
 * Interactive E-Commerce Return Rate Reduction & Risk Score Dashboard
 */

let rawData = null;

// Global Filter State
const state = {
  category: "ALL",
  supplier: "ALL",
  channel: "ALL",
  region: "ALL",
  riskTier: "ALL",
  searchQuery: "",
  sortCol: "avg_predicted_risk_pct",
  sortAsc: false
};

// Colors
const CATEGORY_COLORS = {
  "Apparel & Fashion": "#ef4444",
  "Footwear": "#f97316",
  "Electronics": "#3b82f6",
  "Home & Furniture": "#8b5cf6",
  "Sports & Outdoors": "#06b6d4",
  "Beauty & Personal Care": "#10b981"
};

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("data.json");
    rawData = await res.json();
    
    populateFilterDropdowns();
    attachEventListeners();
    applyFiltersAndRender();
  } catch (err) {
    console.error("Failed to load dashboard data.json:", err);
  }
});

function populateFilterDropdowns() {
  const catSelect = document.getElementById("select-category");
  const suppSelect = document.getElementById("select-supplier");
  const chanSelect = document.getElementById("select-channel");
  const regSelect = document.getElementById("select-region");

  rawData.categories.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.category;
    opt.textContent = `${c.category} (${c.return_rate}%)`;
    catSelect.appendChild(opt);
  });

  rawData.suppliers.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.supplier_name;
    opt.textContent = `${s.supplier_name} (${s.return_rate}%)`;
    suppSelect.appendChild(opt);
  });

  rawData.channels.forEach(ch => {
    const opt = document.createElement("option");
    opt.value = ch.marketing_channel;
    opt.textContent = `${ch.marketing_channel} (${ch.return_rate}%)`;
    chanSelect.appendChild(opt);
  });

  rawData.geography.forEach(g => {
    const opt = document.createElement("option");
    opt.value = g.region;
    opt.textContent = `${g.region} Region (${g.return_rate}%)`;
    regSelect.appendChild(opt);
  });
}

function attachEventListeners() {
  document.getElementById("select-category").addEventListener("change", (e) => {
    state.category = e.target.value;
    applyFiltersAndRender();
  });

  document.getElementById("select-supplier").addEventListener("change", (e) => {
    state.supplier = e.target.value;
    applyFiltersAndRender();
  });

  document.getElementById("select-channel").addEventListener("change", (e) => {
    state.channel = e.target.value;
    applyFiltersAndRender();
  });

  document.getElementById("select-region").addEventListener("change", (e) => {
    state.region = e.target.value;
    applyFiltersAndRender();
  });

  document.getElementById("select-risk-tier").addEventListener("change", (e) => {
    state.riskTier = e.target.value;
    applyFiltersAndRender();
  });

  document.getElementById("product-search-input").addEventListener("input", (e) => {
    state.searchQuery = e.target.value.toLowerCase().trim();
    renderProductTable();
  });

  document.getElementById("btn-reset-filters").addEventListener("click", () => {
    resetAllFilters();
  });

  document.getElementById("btn-export-csv").addEventListener("click", () => {
    exportHighRiskCSV();
  });

  // Table Sort Header Clicks
  document.querySelectorAll("#high-risk-table th[data-sort]").forEach(th => {
    th.addEventListener("click", () => {
      const col = th.getAttribute("data-sort");
      if (state.sortCol === col) {
        state.sortAsc = !state.sortAsc;
      } else {
        state.sortCol = col;
        state.sortAsc = false;
      }
      renderProductTable();
    });
  });

  // Modal Close
  document.getElementById("modal-close-btn").addEventListener("click", closeModal);
  document.getElementById("drill-modal-overlay").addEventListener("click", (e) => {
    if (e.target.id === "drill-modal-overlay") closeModal();
  });
}

function resetAllFilters() {
  state.category = "ALL";
  state.supplier = "ALL";
  state.channel = "ALL";
  state.region = "ALL";
  state.riskTier = "ALL";
  state.searchQuery = "";

  document.getElementById("select-category").value = "ALL";
  document.getElementById("select-supplier").value = "ALL";
  document.getElementById("select-channel").value = "ALL";
  document.getElementById("select-region").value = "ALL";
  document.getElementById("select-risk-tier").value = "ALL";
  document.getElementById("product-search-input").value = "";

  applyFiltersAndRender();
}

function drillThroughCategory(categoryName) {
  state.category = categoryName;
  document.getElementById("select-category").value = categoryName;
  applyFiltersAndRender();
}

function drillThroughSupplier(supplierName) {
  state.supplier = supplierName;
  document.getElementById("select-supplier").value = supplierName;
  applyFiltersAndRender();
}

function drillThroughChannel(channelName) {
  state.channel = channelName;
  document.getElementById("select-channel").value = channelName;
  applyFiltersAndRender();
}

function drillThroughRegion(regionName) {
  state.region = regionName;
  document.getElementById("select-region").value = regionName;
  applyFiltersAndRender();
}

function applyFiltersAndRender() {
  renderActiveTags();
  renderKPIs();
  renderCategoryBars();
  renderSupplierBars();
  renderChannels();
  renderGeography();
  renderReasons();
  renderOddsRatios();
  renderProductTable();
}

function renderActiveTags() {
  const container = document.getElementById("active-tags-container");
  container.innerHTML = "";

  const filterDefs = [
    { key: "category", label: "Category", val: state.category },
    { key: "supplier", label: "Supplier", val: state.supplier },
    { key: "channel", label: "Channel", val: state.channel },
    { key: "region", label: "Region", val: state.region },
    { key: "riskTier", label: "Tier", val: state.riskTier }
  ];

  let hasActive = false;
  filterDefs.forEach(f => {
    if (f.val !== "ALL") {
      hasActive = true;
      const pill = document.createElement("span");
      pill.className = "filter-pill";
      pill.innerHTML = `${f.label}: <strong>${f.val}</strong> &times;`;
      pill.onclick = () => {
        state[f.key] = "ALL";
        document.getElementById(`select-${f.key === "riskTier" ? "risk-tier" : f.key}`).value = "ALL";
        applyFiltersAndRender();
      };
      container.appendChild(pill);
    }
  });

  if (!hasActive) {
    container.innerHTML = `<span style="font-size: 0.78rem; color: #64748b;">Showing unfiltered global dataset (25,000 orders)</span>`;
  }
}

function getFilteredProducts() {
  let list = rawData.all_products;

  if (state.category !== "ALL") {
    list = list.filter(p => p.category === state.category);
  }
  if (state.supplier !== "ALL") {
    list = list.filter(p => p.supplier_name === state.supplier);
  }
  if (state.riskTier === "High Risk") {
    list = list.filter(p => p.avg_predicted_risk_pct >= 45.0);
  } else if (state.riskTier === "Medium Risk") {
    list = list.filter(p => p.avg_predicted_risk_pct >= 25.0 && p.avg_predicted_risk_pct < 45.0);
  } else if (state.riskTier === "Low Risk") {
    list = list.filter(p => p.avg_predicted_risk_pct < 25.0);
  }

  if (state.searchQuery) {
    const q = state.searchQuery;
    list = list.filter(p => 
      p.product_id.toLowerCase().includes(q) ||
      p.product_name.toLowerCase().includes(q) ||
      p.category.toLowerCase().includes(q) ||
      p.supplier_name.toLowerCase().includes(q)
    );
  }

  return list;
}

function renderKPIs() {
  const filteredProds = getFilteredProducts();
  
  let ordersCount = filteredProds.reduce((sum, p) => sum + p.orders, 0);
  let returnsCount = filteredProds.reduce((sum, p) => sum + p.returns, 0);
  let refundedSum = filteredProds.reduce((sum, p) => sum + (p.refunded || 0), 0);
  
  let returnRate = ordersCount > 0 ? ((returnsCount / ordersCount) * 100).toFixed(2) : "0.00";
  let expRiskSum = filteredProds.reduce((sum, p) => sum + ((p.refunded || 1000) * (p.avg_predicted_risk_pct / 100)), 0);

  document.getElementById("kpi-total-orders").textContent = ordersCount.toLocaleString();
  document.getElementById("kpi-return-rate").textContent = `${returnRate}%`;
  document.getElementById("kpi-returns-count").textContent = `${returnsCount.toLocaleString()} returned orders`;
  document.getElementById("kpi-refunded-revenue").textContent = `$${Math.round(refundedSum).toLocaleString()}`;
  document.getElementById("kpi-expected-risk").textContent = `$${Math.round(expRiskSum).toLocaleString()}`;
}

function renderCategoryBars() {
  const container = document.getElementById("category-chart-container");
  container.innerHTML = "";

  rawData.categories.forEach(cat => {
    const isSelected = state.category === cat.category;
    const row = document.createElement("div");
    row.className = "bar-chart-row";
    if (isSelected) row.style.background = "rgba(99, 102, 241, 0.25)";

    const color = CATEGORY_COLORS[cat.category] || "#3b82f6";

    row.innerHTML = `
      <div class="bar-chart-label" title="${cat.category}">${cat.category}</div>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${cat.return_rate}%; background: ${color};"></div>
      </div>
      <div class="bar-chart-val" style="color: ${color};">${cat.return_rate}%</div>
    `;

    row.onclick = () => drillThroughCategory(cat.category);
    container.appendChild(row);
  });
}

function renderSupplierBars() {
  const container = document.getElementById("supplier-chart-container");
  container.innerHTML = "";

  rawData.suppliers.slice(0, 7).forEach(s => {
    const isSelected = state.supplier === s.supplier_name;
    const row = document.createElement("div");
    row.className = "bar-chart-row";
    if (isSelected) row.style.background = "rgba(99, 102, 241, 0.25)";

    const color = s.return_rate >= 40 ? "#ef4444" : s.return_rate >= 25 ? "#f59e0b" : "#10b981";

    row.innerHTML = `
      <div class="bar-chart-label" title="${s.supplier_name}">${s.supplier_name}</div>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${s.return_rate}%; background: ${color};"></div>
      </div>
      <div class="bar-chart-val" style="color: ${color};">${s.return_rate}%</div>
    `;

    row.onclick = () => drillThroughSupplier(s.supplier_name);
    container.appendChild(row);
  });
}

function renderChannels() {
  const container = document.getElementById("channel-container");
  container.innerHTML = "";

  rawData.channels.forEach(ch => {
    const item = document.createElement("div");
    item.className = "channel-item";
    if (state.channel === ch.marketing_channel) item.style.border = "1px solid #6366f1";

    item.innerHTML = `
      <div>
        <div class="channel-name">${ch.marketing_channel}</div>
        <div class="channel-meta">${ch.orders.toLocaleString()} orders | ${ch.avg_discount_pct}% avg discount</div>
      </div>
      <div class="channel-rate">${ch.return_rate}%</div>
    `;
    item.onclick = () => drillThroughChannel(ch.marketing_channel);
    container.appendChild(item);
  });
}

function renderGeography() {
  const container = document.getElementById("geography-container");
  container.innerHTML = `<div class="geo-grid-compact"></div>`;
  const grid = container.querySelector(".geo-grid-compact");

  rawData.geography.forEach(g => {
    const card = document.createElement("div");
    card.className = "geo-region-card";
    if (state.region === g.region) card.style.borderColor = "#6366f1";

    card.innerHTML = `
      <div class="geo-region-name">${g.region} Region</div>
      <div class="geo-region-val">${g.return_rate}%</div>
      <div class="geo-region-sub">Avg delay: +${g.avg_delay} days</div>
    `;
    card.onclick = () => drillThroughRegion(g.region);
    grid.appendChild(card);
  });
}

function renderReasons() {
  const container = document.getElementById("reasons-container");
  container.innerHTML = "";

  rawData.reasons.slice(0, 5).forEach(r => {
    const row = document.createElement("div");
    row.className = "reason-row";
    row.innerHTML = `
      <span class="reason-name">${r.reason}</span>
      <span class="reason-count-badge">${r.count.toLocaleString()} returns</span>
    `;
    container.appendChild(row);
  });
}

function renderOddsRatios() {
  const container = document.getElementById("odds-container");
  container.innerHTML = "";

  rawData.top_features.slice(0, 6).forEach(f => {
    const isRiskUp = f.odds_ratio > 1.0;
    const card = document.createElement("div");
    card.className = `odds-card ${isRiskUp ? "risk-up" : "risk-down"}`;

    const displayName = f.feature
      .replace("category_", "Cat: ")
      .replace("marketing_channel_", "Channel: ")
      .replace("payment_method_", "Payment: ")
      .replace("delivery_delay_days", "Shipping Delay Days");

    const interp = isRiskUp
      ? `+${((f.odds_ratio - 1) * 100).toFixed(0)}% return odds multiplier`
      : `-${((1 - f.odds_ratio) * 100).toFixed(0)}% lower return odds`;

    card.innerHTML = `
      <div class="odds-feat-name" title="${f.feature}">${displayName}</div>
      <div class="odds-val-row">
        <span class="odds-ratio-number">${f.odds_ratio.toFixed(2)}x</span>
        <span class="odds-interpretation">${interp}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderProductTable() {
  const tbody = document.getElementById("high-risk-tbody");
  tbody.innerHTML = "";

  let prods = getFilteredProducts();

  // Sort
  prods.sort((a, b) => {
    let va = a[state.sortCol];
    let vb = b[state.sortCol];
    if (typeof va === "string") va = va.toLowerCase();
    if (typeof vb === "string") vb = vb.toLowerCase();
    if (va < vb) return state.sortAsc ? -1 : 1;
    if (va > vb) return state.sortAsc ? 1 : -1;
    return 0;
  });

  document.getElementById("product-count-badge").textContent = `${prods.length} Products Filtered`;

  prods.forEach(p => {
    const tr = document.createElement("tr");

    let riskBadgeClass = "badge-risk-elevated";
    if (p.avg_predicted_risk_pct >= 50.0) riskBadgeClass = "badge-risk-critical";
    else if (p.avg_predicted_risk_pct >= 40.0) riskBadgeClass = "badge-risk-severe";

    tr.innerHTML = `
      <td><strong>${p.product_id}</strong></td>
      <td>${p.product_name}</td>
      <td><span style="color: ${CATEGORY_COLORS[p.category] || '#94a3b8'}; font-weight: 600;">${p.category}</span></td>
      <td>${p.supplier_name}</td>
      <td class="text-right">$${p.unit_price.toFixed(2)}</td>
      <td class="text-right"><strong>${p.actual_return_rate_pct}%</strong></td>
      <td class="text-right"><span class="badge-risk ${riskBadgeClass}">${p.avg_predicted_risk_pct}%</span></td>
      <td class="text-right">$${Math.round(p.refunded || 0).toLocaleString()}</td>
      <td><span style="color: #cbd5e1;">${p.primary_return_reason}</span></td>
      <td><span class="action-playbook-tag">${p.recommended_mitigation_action}</span></td>
      <td class="text-center">
        <button class="btn-inspect" onclick="openProductModal('${p.product_id}')">Drill</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function openProductModal(productId) {
  const prod = rawData.all_products.find(p => p.product_id === productId);
  if (!prod) return;

  document.getElementById("modal-sku-badge").textContent = prod.product_id;
  document.getElementById("modal-product-title").textContent = prod.product_name;

  const content = document.getElementById("modal-body-content");
  content.innerHTML = `
    <div class="modal-metrics-grid">
      <div class="modal-metric-card">
        <div class="modal-metric-title">Actual Return Rate</div>
        <div class="modal-metric-val" style="color: #f87171;">${prod.actual_return_rate_pct}%</div>
      </div>
      <div class="modal-metric-card">
        <div class="modal-metric-title">Predicted Risk %</div>
        <div class="modal-metric-val" style="color: #a855f7;">${prod.avg_predicted_risk_pct}%</div>
      </div>
      <div class="modal-metric-card">
        <div class="modal-metric-title">Total Refunded</div>
        <div class="modal-metric-val" style="color: #fbbf24;">$${Math.round(prod.refunded || 0).toLocaleString()}</div>
      </div>
    </div>

    <div style="margin-bottom: 1rem; font-size: 0.85rem; color: #cbd5e1;">
      <p><strong>Category:</strong> ${prod.category} | <strong>Subcategory:</strong> ${prod.subcategory}</p>
      <p><strong>Supplier:</strong> ${prod.supplier_name} | <strong>Unit Price:</strong> $${prod.unit_price.toFixed(2)}</p>
      <p><strong>Primary Root Cause:</strong> <span style="color: #f87171; font-weight: 600;">${prod.primary_return_reason}</span></p>
    </div>

    <div class="modal-playbook-box">
      <h4>Actionable Mitigation Strategy</h4>
      <p>${prod.recommended_mitigation_action}</p>
    </div>
  `;

  document.getElementById("drill-modal-overlay").classList.add("active");
}

function closeModal() {
  document.getElementById("drill-modal-overlay").classList.remove("active");
}

function exportHighRiskCSV() {
  const prods = getFilteredProducts();
  if (!prods.length) {
    alert("No products match the active filter criteria.");
    return;
  }

  const headers = ["product_id", "product_name", "category", "supplier_name", "unit_price", "actual_return_rate_pct", "avg_predicted_risk_pct", "total_refund_amount", "primary_return_reason", "recommended_mitigation_action"];
  
  let csvContent = headers.join(",") + "\n";
  prods.forEach(p => {
    const row = [
      `"${p.product_id}"`,
      `"${p.product_name}"`,
      `"${p.category}"`,
      `"${p.supplier_name}"`,
      p.unit_price,
      p.actual_return_rate_pct,
      p.avg_predicted_risk_pct,
      Math.round(p.refunded || 0),
      `"${p.primary_return_reason}"`,
      `"${p.recommended_mitigation_action}"`
    ];
    csvContent += row.join(",") + "\n";
  });

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `high_risk_products_filtered_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
