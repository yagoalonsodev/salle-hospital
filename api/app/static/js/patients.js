/** Vista: gestión de pacientes (solo fetch + DOM). */

const $p = (sel) => document.querySelector(sel);

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function patientLabel(p) {
  return (p.display_name && String(p.display_name).trim()) || p.patient_id;
}

let patientsCache = [];
let selectedPatientId = null;

async function apiPatients(method, path = "", body = null) {
  const opts = { method, headers: { Accept: "application/json" } };
  if (body) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(`/api/patients${path}`, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function showFormError(msg) {
  const el = $p("#patient-form-error");
  if (!msg) {
    el.classList.add("hidden");
    return;
  }
  el.textContent = msg;
  el.classList.remove("hidden");
}

function openPatientForm(mode, patient = null) {
  $p("#patient-form-card").classList.remove("hidden");
  $p("#pf-mode").value = mode;
  $p("#patient-form-title").textContent =
    mode === "edit" ? "Editar paciente" : "Nuevo paciente";
  const submitBtn = $p("#patient-form button[type=submit]");
  if (submitBtn) {
    submitBtn.textContent = mode === "edit" ? "Guardar" : "Crear y subir radiografía";
  }
  $p("#pf-name").value = patient?.display_name || "";
  $p("#pf-sex").value = patient?.sex || "X";
  $p("#pf-age").value = patient?.age_range || "";
  $p("#pf-site").value = patient?.site_code || "";
  showFormError(null);
}

async function loadSites() {
  try {
    const res = await fetch("/api/sites");
    const data = await res.json();
    const sel = $p("#pf-site");
    const current = sel.value;
    sel.innerHTML =
      '<option value="">— Selecciona centro —</option>' +
      (data.sites || [])
        .map(
          (s) =>
            `<option value="${escapeHtml(s.site_code)}">${escapeHtml(s.site_name)}</option>`
        )
        .join("");
    if (current) sel.value = current;
  } catch (err) {
    showFormError(`No se pudieron cargar los centros: ${err.message}`);
  }
}

function closePatientForm() {
  $p("#patient-form-card").classList.add("hidden");
  showFormError(null);
}

function renderPatientsList() {
  const list = $p("#patients-list");
  const empty = $p("#patients-empty");
  const loading = $p("#patients-loading");

  loading.classList.add("hidden");

  if (!patientsCache.length) {
    list.innerHTML = "";
    empty.classList.remove("hidden");
    return;
  }

  empty.classList.add("hidden");
  list.innerHTML = patientsCache
    .map(
      (p) => `
    <li class="patient-item" data-id="${escapeHtml(p.patient_id)}">
      <div>
        <strong>${escapeHtml(patientLabel(p))}</strong>
        <div class="meta">${escapeHtml(p.sex)} · ${escapeHtml(p.age_range)} · ${escapeHtml(p.site_name || p.site_code)}</div>
      </div>
      <span class="chip">${p.study_count} RX</span>
    </li>`
    )
    .join("");

  list.querySelectorAll(".patient-item").forEach((el) => {
    el.addEventListener("click", () => selectPatient(el.dataset.id));
  });
}

async function loadPatients() {
  $p("#patients-loading").classList.remove("hidden");
  try {
    const data = await apiPatients("GET");
    patientsCache = data.patients || [];
    renderPatientsList();
    if (window.refreshPatientSelect) window.refreshPatientSelect(patientsCache);
    if (selectedPatientId) await selectPatient(selectedPatientId);
  } catch (err) {
    $p("#patients-loading").textContent = err.message;
  }
}

async function selectPatient(patientId) {
  selectedPatientId = patientId;
  try {
    const p = await apiPatients("GET", `/${encodeURIComponent(patientId)}`);
    $p("#patient-detail").classList.remove("hidden");
    $p("#detail-title").textContent = patientLabel(p);
    $p("#detail-study-count").textContent = String(p.study_count);

    $p("#detail-meta").innerHTML = `
      <div><dt>Sexo</dt><dd>${p.sex}</dd></div>
      <div><dt>Edad</dt><dd>${p.age_range}</dd></div>
      <div><dt>Centro</dt><dd>${escapeHtml(p.site_name || p.site_code)}</dd></div>
      <div><dt>Alta</dt><dd>${new Date(p.created_at).toLocaleString("es-ES")}</dd></div>
    `;

    const studies = p.studies || [];
    const ul = $p("#detail-studies");
    ul.innerHTML = studies.length
      ? studies
          .map((s) => {
            const pred = s.predicted_label
              ? ` · IA: <strong>${s.predicted_label}</strong>`
              : " · sin predicción";
            const when = s.ingested_at
              ? new Date(s.ingested_at).toLocaleString("es-ES")
              : "—";
            return `<li><strong>${when}</strong>${pred}</li>`;
          })
          .join("")
      : "<li class='hint'>Sin radiografías asociadas</li>";
  } catch (err) {
    showFormError(err.message);
  }
}

$p("#btn-new-patient")?.addEventListener("click", () => openPatientForm("create"));
$p("#btn-cancel-patient")?.addEventListener("click", closePatientForm);

$p("#patient-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const mode = $p("#pf-mode").value;
  const body = {
    display_name: $p("#pf-name").value.trim(),
    sex: $p("#pf-sex").value,
    age_range: $p("#pf-age").value.trim(),
    site_code: $p("#pf-site").value.trim(),
  };

  try {
    if (mode === "edit" && selectedPatientId) {
      await apiPatients("PUT", `/${encodeURIComponent(selectedPatientId)}`, body);
    } else {
      const created = await apiPatients("POST", "", body);
      selectedPatientId = created.patient_id;
      closePatientForm();
      if (window.openUploadForPatient) window.openUploadForPatient(created);
      await loadPatients();
      return;
    }
    closePatientForm();
    await loadPatients();
  } catch (err) {
    showFormError(err.message);
  }
});

$p("#btn-upload-rx")?.addEventListener("click", async () => {
  if (!selectedPatientId || !window.openUploadForPatient) return;
  let p = patientsCache.find((x) => x.patient_id === selectedPatientId);
  if (!p) {
    try {
      p = await apiPatients("GET", `/${encodeURIComponent(selectedPatientId)}`);
    } catch {
      return;
    }
  }
  window.openUploadForPatient(p, { openFilePicker: true });
});

$p("#btn-edit-patient")?.addEventListener("click", async () => {
  if (!selectedPatientId) return;
  const p = patientsCache.find((x) => x.patient_id === selectedPatientId);
  if (p) openPatientForm("edit", p);
  else {
    const full = await apiPatients("GET", `/${encodeURIComponent(selectedPatientId)}`);
    openPatientForm("edit", full);
  }
});

$p("#btn-delete-patient")?.addEventListener("click", async () => {
  if (!selectedPatientId) return;
  const p = patientsCache.find((x) => x.patient_id === selectedPatientId);
  const n = p?.study_count ?? 0;
  let cascade = false;
  if (n > 0) {
    const ok = confirm(
      `Este paciente tiene ${n} radiografía(s). ¿Eliminar paciente y todas sus RX?`
    );
    if (!ok) return;
    cascade = true;
  } else if (!confirm(`¿Eliminar a ${patientLabel(p || { patient_id: selectedPatientId })}?`)) {
    return;
  }

  try {
    const q = cascade ? "?cascade_studies=true" : "";
    await apiPatients("DELETE", `/${encodeURIComponent(selectedPatientId)}${q}`);
    selectedPatientId = null;
    $p("#patient-detail").classList.add("hidden");
    await loadPatients();
  } catch (err) {
    alert(err.message);
  }
});

window.loadPatients = loadPatients;
window.getSelectedPatientId = () => selectedPatientId;
document.addEventListener("DOMContentLoaded", () => {
  loadSites();
  loadPatients();
});
