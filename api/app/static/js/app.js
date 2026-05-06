/** Vista: navegación, métricas y subida de radiografías. */

const $ = (sel) => document.querySelector(sel);

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"];
const MAX_BYTES = 10 * 1024 * 1024;

let selectedFile = null;
let patientsById = {};

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function pct(v) {
  return `${(Number(v) * 100).toFixed(1)}%`;
}

function showUploadError(msg) {
  const el = $("#upload-error");
  if (!msg) {
    el.classList.add("hidden");
    return;
  }
  el.textContent = msg;
  el.classList.remove("hidden");
}

function patientOptionLabel(p) {
  const name =
    (p.display_name && String(p.display_name).trim()) || p.patient_id;
  return `${name} (${p.study_count ?? 0} RX)`;
}

window.refreshPatientSelect = (patients) => {
  patientsById = {};
  (patients || []).forEach((p) => {
    patientsById[p.patient_id] = p;
  });
  const sel = $("#upload-patient-id");
  const current = sel.value;
  sel.innerHTML =
    '<option value="">— Selecciona un paciente —</option>' +
    (patients || [])
      .map(
        (p) =>
          `<option value="${p.patient_id}">${patientOptionLabel(p)}</option>`
      )
      .join("");
  if (current) sel.value = current;
  if (sel.value) loadPatientRadiographs(sel.value);
};

function switchPanel(panelId) {
  document.querySelectorAll(".segment").forEach((b) => {
    b.classList.toggle("active", b.dataset.panel === panelId);
  });
  document.querySelectorAll(".panel").forEach((p) => {
    const isActive = p.id === `panel-${panelId}`;
    p.classList.toggle("active", isActive);
    p.classList.toggle("hidden", !isActive);
  });
  if (panelId === "metrics") loadMetrics();
  if (panelId === "upload") {
    let pid = $("#upload-patient-id")?.value;
    if (!pid && window.getSelectedPatientId?.()) {
      pid = window.getSelectedPatientId();
      $("#upload-patient-id").value = pid;
    }
    if (pid) loadPatientRadiographs(pid);
  }
}

function resetUploadForm() {
  selectedFile = null;
  showUploadError(null);
  $("#result")?.classList.add("hidden");
  $("#preview-wrap")?.classList.add("hidden");
  if (fileInput) fileInput.value = "";
}

function setUploadPatient(patient) {
  const sel = $("#upload-patient-id");
  if (!sel || !patient?.patient_id) return;
  let opt = sel.querySelector(`option[value="${patient.patient_id}"]`);
  if (!opt) {
    opt = document.createElement("option");
    opt.value = patient.patient_id;
    opt.textContent = patientOptionLabel({
      ...patient,
      study_count: patient.study_count ?? 0,
    });
    sel.appendChild(opt);
  }
  sel.value = patient.patient_id;
  patientsById[patient.patient_id] = patient;
  loadPatientRadiographs(patient.patient_id);
}

function showUploadHint(message) {
  const hint = $("#upload-hint");
  if (!hint) return;
  if (!message) {
    hint.classList.add("hidden");
    hint.textContent = "";
    return;
  }
  hint.textContent = message;
  hint.classList.remove("hidden");
}

function renderRxCard(study) {
  const label = study.predicted_label || "—";
  const conf = study.confidence != null ? pct(study.confidence) : "";
  const predLine = conf ? `${label} · ${conf}` : label;
  const imgUrl = study.minio_object_key
    ? `/api/studies/${encodeURIComponent(study.study_id)}/image`
    : "";
  return `
    <li>
      <article class="rx-card">
        ${imgUrl ? `<img src="${imgUrl}" alt="Radiografía ${escapeHtml(study.study_id)}" loading="lazy" />` : ""}
        <div class="rx-card-body">
          <p class="rx-id">${escapeHtml(study.study_id)}</p>
          <p class="rx-pred label-main ${escapeHtml(label)}">${escapeHtml(predLine)}</p>
        </div>
      </article>
    </li>`;
}

async function loadPatientRadiographs(patientId) {
  const panel = $("#patient-rx-panel");
  const gallery = $("#patient-rx-gallery");
  const empty = $("#patient-rx-empty");
  const labelEl = $("#upload-patient-label");

  if (!patientId) {
    panel?.classList.add("hidden");
    return;
  }

  const cached = patientsById[patientId];
  const displayName =
    (cached?.display_name && String(cached.display_name).trim()) || patientId;
  labelEl.textContent = displayName;
  panel.classList.remove("hidden");
  gallery.innerHTML = "<li class='hint'>Cargando…</li>";
  empty.classList.add("hidden");

  try {
    const res = await fetch(`/api/patients/${encodeURIComponent(patientId)}`);
    const patient = await res.json();
    if (!res.ok) throw new Error(patient.error || res.statusText);

    patientsById[patientId] = patient;
    const studies = patient.studies || [];

    if (!studies.length) {
      gallery.innerHTML = "";
      empty.classList.remove("hidden");
      return;
    }

    gallery.innerHTML = studies.map((s) => renderRxCard(s)).join("");
  } catch (err) {
    gallery.innerHTML = "";
    empty.textContent = err.message;
    empty.classList.remove("hidden");
  }
}

window.loadPatientRadiographs = loadPatientRadiographs;

window.openUploadForPatient = (patient, { openFilePicker = true } = {}) => {
  const id = typeof patient === "string" ? patient : patient?.patient_id;
  const name =
    typeof patient === "object"
      ? (patient.display_name && String(patient.display_name).trim()) ||
        patient.patient_id
      : id;

  switchPanel("upload");
  if (typeof patient === "object") setUploadPatient(patient);
  else if (id) {
    $("#upload-patient-id").value = id;
    loadPatientRadiographs(id);
  }

  resetUploadForm();
  showUploadHint(
    name ? `Paciente «${name}». Elige o arrastra la radiografía.` : null
  );
  dropZone?.focus();

  if (openFilePicker) {
    requestAnimationFrame(() => fileInput?.click());
  }
};

document.querySelectorAll(".segment").forEach((btn) => {
  btn.addEventListener("click", () => {
    switchPanel(btn.dataset.panel);
    if (btn.dataset.panel === "upload") showUploadHint(null);
  });
});

$("#upload-patient-id")?.addEventListener("change", (e) => {
  loadPatientRadiographs(e.target.value);
});

function validateClientFile(file) {
  if (!file) return "Selecciona una imagen";
  if (!ALLOWED_TYPES.includes(file.type) && !/\.(jpe?g|png)$/i.test(file.name)) {
    return "Solo JPG o PNG";
  }
  if (file.size > MAX_BYTES) return "Máximo 10 MB";
  return null;
}

function setFile(file) {
  const err = validateClientFile(file);
  if (err) {
    showUploadError(err);
    selectedFile = null;
    return;
  }
  showUploadError(null);
  selectedFile = file;
  $("#preview").src = URL.createObjectURL(file);
  $("#preview-wrap").classList.remove("hidden");
}

const dropZone = $("#drop-zone");
const fileInput = $("#file-input");

dropZone?.addEventListener("click", () => fileInput.click());
fileInput?.addEventListener("change", () => setFile(fileInput.files[0]));

dropZone?.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone?.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone?.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    setFile(file);
  }
});

function renderResult(data) {
  const probs = data.probabilities || {};
  const label = data.predicted_label || "—";
  const colors = { covid: "#bf5af2", neumonia: "#ff9f0a", sana: "#30d158" };

  const bars = ["covid", "neumonia", "sana"]
    .map((k) => {
      const v = probs[k] || 0;
      return `<div class="prob-row">
        <span>${k}</span>
        <div class="prob-bar"><div class="prob-fill" style="width:${pct(v)};background:${colors[k]}"></div></div>
        <span>${pct(v)}</span>
      </div>`;
    })
    .join("");

  const el = $("#result");
  el.innerHTML = `
    <p class="study-id">${escapeHtml(data.study_id || "—")}</p>
    <p class="label-main ${escapeHtml(label)}">${escapeHtml(label)}</p>
    <p class="hint">Confianza ${pct(data.confidence || 0)}</p>
    <div style="margin-top:0.75rem">${bars}</div>
    <p class="hint" style="margin-top:0.75rem">Guardada en MinIO. Aparece abajo en la galería del paciente.</p>
  `;
  el.classList.remove("hidden");
  el.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

$("#upload-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  showUploadError(null);
  $("#result").classList.add("hidden");

  const patientId = $("#upload-patient-id").value;
  if (!patientId) {
    showUploadError("Selecciona un paciente");
    return;
  }
  if (!selectedFile) {
    showUploadError("Selecciona una radiografía");
    return;
  }

  const form = new FormData();
  form.append("file", selectedFile);
  form.append("patient_id", patientId);

  const btn = $("#submit-btn");
  btn.disabled = true;
  btn.textContent = "Analizando…";

  try {
    const res = await fetch("/upload", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    renderResult(data);
    resetUploadForm();
    await loadPatientRadiographs(patientId);
    if (window.loadPatients) await window.loadPatients();
    loadMetrics();
  } catch (err) {
    showUploadError(err.message || "Error al analizar");
  } finally {
    btn.disabled = false;
    btn.textContent = "Analizar";
  }
});

async function loadHealth() {
  const badge = $("#health-badge");
  try {
    const res = await fetch("/health");
    const data = await res.json();
    const ok = data.status === "ok";
    badge.textContent = ok ? "Sistema listo" : "Degradado";
    badge.className = `status-pill ${ok ? "ok" : "warn"}`;
  } catch {
    badge.textContent = "Sin conexión";
    badge.className = "status-pill warn";
  }
}

function renderSummaryItem(r) {
  const label = r.predicted_label || "—";
  const conf = r.confidence != null ? pct(r.confidence) : "";
  const when = r.inferred_at
    ? new Date(r.inferred_at).toLocaleString("es-ES")
    : "";
  return `
    <li class="summary-item">
      <p class="study-id">${escapeHtml(r.study_id)}</p>
      <p class="study-pred label-main ${escapeHtml(label)}">${escapeHtml(label)}${conf ? ` · ${conf}` : ""}</p>
      <p class="study-meta">${escapeHtml(r.patient_name || "—")}${when ? ` · ${when}` : ""}</p>
    </li>`;
}

async function loadMetrics() {
  const panel = $("#metrics-panel");
  try {
    const res = await fetch("/metrics");
    const data = await res.json();
    panel.innerHTML = `
      <div class="metric-tile"><strong>${data.predictions_total ?? 0}</strong><span>Predicciones</span></div>
      <div class="metric-tile"><strong>${data.api_uploads ?? 0}</strong><span>Subidas API</span></div>
      <div class="metric-tile"><strong>${data.patients_total ?? 0}</strong><span>Pacientes</span></div>
      <div class="metric-tile"><strong>${data.model_version || "—"}</strong><span>Modelo activo</span></div>
    `;

    const recent = data.recent_predictions || [];
    const list = $("#summary-list");
    const empty = $("#summary-empty");
    if (!recent.length) {
      list.innerHTML = "";
      empty.classList.remove("hidden");
    } else {
      empty.classList.add("hidden");
      list.innerHTML = recent.map(renderSummaryItem).join("");
    }
  } catch {
    panel.innerHTML = "<p class='hint'>No se pudieron cargar métricas</p>";
  }
}

loadHealth();
loadMetrics();
