const API_BASE = "http://localhost:5000/api";

async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

/* ---------- Nav ---------- */
document.querySelectorAll(".nav-item").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b === btn));
    document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.dataset.view === btn.dataset.view));
    if (btn.dataset.view === "garage") loadGarages();
    if (btn.dataset.view === "requests") loadRequests();
    if (btn.dataset.view === "alerts") loadActivity();
    if (btn.dataset.view === "help") loadHelp();
  });
});

/* ---------- helpers to classify a raw Property.presentation() dict ---------- */
function kindOf(asset) {
  if ("residence_id" in asset) return "Residence";
  if ("garage_id" in asset) return "Garage";
  if ("building_id" in asset) return "Building";
  return "Property";
}
function idOf(asset) {
  return asset.residence_id ?? asset.garage_id ?? asset.building_id;
}

/* ---------- Assets ---------- */
const assetType = document.getElementById("asset-type");
const assetFields = document.getElementById("asset-fields");

function renderAssetFields() {
  const t = assetType.value;
  if (t === "residence") {
    assetFields.innerHTML = `
      <label>Location<input type="text" id="f-location" placeholder="Uptown" required /></label>
      <label>Area<input type="text" id="f-area" placeholder="95 sqm" required /></label>`;
  } else if (t === "garage") {
    assetFields.innerHTML = `<label>Capacity<input type="number" id="f-capacity" min="1" value="2" required /></label>`;
  } else {
    assetFields.innerHTML = `
      <label>Houses<input type="number" id="f-houses" min="1" value="6" required /></label>
      <label>Floors<input type="number" id="f-floors" min="1" value="3" required /></label>`;
  }
}
assetType.addEventListener("change", renderAssetFields);
renderAssetFields();

document.getElementById("asset-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("asset-id").value.trim();
  const t = assetType.value;
  try {
    if (t === "residence") {
      await api("/assets/residence", { method: "POST", body: {
        id, location: document.getElementById("f-location").value, area: document.getElementById("f-area").value,
      }});
    } else if (t === "garage") {
      await api("/assets/garage", { method: "POST", body: {
        id, capacity: document.getElementById("f-capacity").value,
      }});
    } else {
      await api("/assets/building", { method: "POST", body: {
        id, n_house: document.getElementById("f-houses").value, n_floor: document.getElementById("f-floors").value,
      }});
    }
    e.target.reset();
    renderAssetFields();
    loadAssets();
  } catch (err) {
    alert(err.message);
  }
});

document.getElementById("detail-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("detail-id").value.trim();
  const detail = document.getElementById("detail-text").value.trim();
  try {
    await api(`/assets/${encodeURIComponent(id)}/detail`, { method: "POST", body: { detail } });
    e.target.reset();
    loadAssets();
  } catch (err) {
    alert(err.message);
  }
});

async function loadAssets() {
  const assets = await api("/assets");
  const grid = document.getElementById("assets-grid");
  if (!assets.length) { grid.innerHTML = "<p class='empty-note'>No assets yet.</p>"; return; }
  grid.innerHTML = assets.map((a) => {
    const kind = kindOf(a);
    let extra = "";
    if (kind === "Garage") extra = `<li>Capacity: ${a.capacity} · Cars: ${a.cars.length}</li>`;
    if (kind === "Residence") extra = `<li>${a.location} · ${a.area}</li>`;
    if (kind === "Building") extra = `<li>${a.number_of_houses} houses · ${a.number_of_floors} floors</li>`;
    const details = (a.details || []).map((d) => `<li>${d}</li>`).join("");
    return `<div class="asset-card">
      <span class="asset-kind">${kind}</span>
      <p class="asset-id">${idOf(a)}</p>
      <ul class="asset-detail-list">${extra}${details}</ul>
    </div>`;
  }).join("");
}

/* ---------- Garage door ---------- */
async function loadGarages() {
  const assets = await api("/assets");
  const garages = assets.filter((a) => "garage_id" in a);

  document.getElementById("car-garage").innerHTML = garages.map((g) => `<option value="${g.garage_id}">${g.garage_id}</option>`).join("");

  const container = document.getElementById("garage-panels");
  container.innerHTML = garages.map((g) => `
    <div class="access-panel">
      <div class="access-panel-top">
        <div>
          <div class="access-panel-name">${g.garage_id}</div>
          <div class="access-panel-meta">CAPACITY ${g.capacity} · ${g.cars.length} PARKED</div>
          <div class="status-light-row">
            <span class="status-light" id="light-${g.garage_id}"></span>
            <span class="status-text" id="status-text-${g.garage_id}">Checking…</span>
          </div>
        </div>
        <button class="access-toggle" id="toggle-${g.garage_id}">Toggle door</button>
      </div>
      <div class="door-viewport">
        <div class="door-frame"></div>
        <div class="door-panel" id="door-${g.garage_id}"></div>
        <span class="door-label">${g.garage_id} // REMOTE_CONTROL</span>
      </div>
      <div class="cars-row">${g.cars.map((c) => `<span class="car-chip">${c}</span>`).join("") || "<span class='empty-note'>No cars parked.</span>"}</div>
    </div>`).join("");

  for (const g of garages) {
    await refreshDoorStatus(g.garage_id);
    document.getElementById(`toggle-${g.garage_id}`).addEventListener("click", () => toggleDoor(g.garage_id));
  }
}

async function refreshDoorStatus(garageId) {
  const status = await api(`/garages/${garageId}/door`);
  applyDoorState(garageId, status.is_open);
}

function applyDoorState(garageId, isOpen) {
  document.getElementById(`light-${garageId}`).className = `status-light ${isOpen ? "open" : ""}`;
  document.getElementById(`status-text-${garageId}`).textContent = isOpen ? "Open" : "Closed";
  document.getElementById(`door-${garageId}`).classList.toggle("open", isOpen);
}

async function toggleDoor(garageId) {
  const btn = document.getElementById(`toggle-${garageId}`);
  const light = document.getElementById(`light-${garageId}`);
  const text = document.getElementById(`status-text-${garageId}`);
  const current = light.classList.contains("open");
  const command = current ? "close" : "open";

  btn.disabled = true;
  light.className = "status-light moving";
  text.textContent = "Moving…"; // this genuinely waits on Controller's real time.sleep(1)
  try {
    const result = await api(`/garages/${garageId}/door`, { method: "POST", body: { command } });
    applyDoorState(garageId, result.is_open);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById("car-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const garageId = document.getElementById("car-garage").value;
  const car = document.getElementById("car-id").value.trim();
  try {
    const result = await api(`/garages/${garageId}/cars`, { method: "POST", body: { car } });
    if (result.message.startsWith("ALERT")) alert(result.message);
    e.target.reset();
    loadGarages();
  } catch (err) {
    alert(err.message);
  }
});

/* ---------- Parking requests ---------- */
async function loadRequests() {
  const levels = await api("/requests");
  const grid = document.getElementById("levels-grid");
  grid.innerHTML = Object.entries(levels)
    .filter(([lvl, cars]) => cars.length || Number(lvl) <= 6)
    .map(([lvl, cars]) => `
      <div class="level-slot ${cars.length ? "occupied" : ""}">
        <div class="level-num">Level ${lvl}</div>
        <div class="level-cars">${cars.join(", ") || "—"}</div>
      </div>`).join("");
}

document.getElementById("request-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const car_id = document.getElementById("req-car").value.trim();
  const level = document.getElementById("req-level").value;
  await api("/requests", { method: "POST", body: { car_id, level } });
  e.target.reset();
  document.getElementById("req-level").value = 1;
  loadRequests();
});

/* ---------- Account ---------- */
document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const result = await api("/account/login", { method: "POST", body: {
    name: document.getElementById("acc-name").value.trim(),
    email: document.getElementById("acc-email").value.trim(),
    phone: document.getElementById("acc-phone").value.trim(),
    house_id: document.getElementById("acc-house").value.trim(),
  }});
  const pill = document.getElementById("login-pill");
  pill.textContent = result.logged_in ? `Signed in as ${result.account.name}` : "Sign-in failed";
  pill.className = `status-pill ${result.logged_in ? "on" : "off"}`;
});

document.getElementById("edit-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/account", { method: "PUT", body: {
    name: document.getElementById("edit-name").value.trim(),
    phone: document.getElementById("edit-phone").value.trim(),
    email: document.getElementById("edit-email").value.trim(),
  }});
  e.target.reset();
});

/* ---------- Alerts / Notifications ---------- */
document.getElementById("notify-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/notify", { method: "POST", body: {
    car_id: document.getElementById("notify-car").value.trim(),
    garage_id: document.getElementById("notify-garage").value.trim(),
  }});
  e.target.reset();
  loadActivity();
});

document.getElementById("alert-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/alert", { method: "POST", body: {
    problem: document.getElementById("alert-problem").value.trim(),
  }});
  e.target.reset();
  loadActivity();
});

async function loadActivity() {
  const items = await api("/activity");
  const feed = document.getElementById("alerts-feed");
  feed.innerHTML = items.map((item) => `<div class="feed-item ${item.kind}">${item.message}</div>`).join("") || "<p class='empty-note'>No activity yet.</p>";
}

/* ---------- Help desk ---------- */
document.getElementById("help-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/help", { method: "POST", body: {
    car_id: document.getElementById("help-car").value.trim(),
    payment_state: document.getElementById("help-payment").value,
    car_state: document.getElementById("help-carstate").value,
    rental_value: document.getElementById("help-rental").value.trim(),
  }});
  e.target.reset();
  loadHelp();
});

async function loadHelp() {
  const records = await api("/help");
  const list = document.getElementById("help-list");
  list.innerHTML = records.map((r) => `
    <div class="help-card">
      <div class="help-card-top"><span class="help-car">${r.car_id}</span></div>
      <div class="help-fields">
        <div class="help-field"><span>Payment</span>${r.payment_state}</div>
        <div class="help-field"><span>Car state</span>${r.car_state}</div>
        <div class="help-field"><span>Rental value</span>${r.rental_value}</div>
      </div>
    </div>`).join("") || "<p class='empty-note'>No help records yet.</p>";
}

/* ---------- Boot ---------- */
loadAssets();
loadGarages();
