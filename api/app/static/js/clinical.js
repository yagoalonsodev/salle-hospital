/** Vista: diagnóstico por síntomas (dataset textual 100k). */

const $c = (sel) => document.querySelector(sel);

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const DIAG_LABELS = {
  sana: "Sin patología destacada",
  neumonia: "Neumonía",
  covid: "COVID-19",
  gripe: "Gripe",
  asma: "Asma",
  bronquitis: "Bronquitis",
  epoc: "EPOC",
  rinitis_alergica: "Rinitis alérgica",
};

function diagClass(name) {
  return String(name || "")
    .toLowerCase()
    .replace(/[^a-z0-9_]/g, "_");
}

function formatDiagnosis(name) {
  return DIAG_LABELS[name] || String(name).replace(/_/g, " ");
}

window.formatDiagnosis = formatDiagnosis;

function renderProbBars(probs) {
  if (!probs || typeof probs !== "object") return "";
  const sorted = Object.entries(probs).sort((a, b) => b[1] - a[1]).slice(0, 5);
  return sorted
    .map(([label, p]) => {
      const pct = Math.round(Number(p) * 100);
      return `
        <div class="prob-row">
          <span>${escapeHtml(formatDiagnosis(label))}</span>
          <div class="prob-bar"><div class="prob-fill diag-${diagClass(label)}" style="width:${pct}%"></div></div>
          <span>${pct}%</span>
        </div>`;
    })
    .join("");
}

function showClinicalError(msg) {
  const el = $c("#clinical-error");
  if (!msg) {
    el.classList.add("hidden");
    return;
  }
  el.textContent = msg;
  el.classList.remove("hidden");
}

function renderClinicalResult(data) {
  const box = $c("#clinical-result");
  const pred = data.predicted_diagnosis;
  const probs = data.probabilities || data.prob_json;
  box.innerHTML = `
    <p class="result-kicker">Predicción del modelo clínico</p>
    <p class="label-main diag-${diagClass(pred)}">${escapeHtml(formatDiagnosis(pred))}</p>
    <p class="hint">Paciente: ${escapeHtml(data.patient_display_name || data.patient_id || "")}</p>
    ${renderProbBars(probs)}
  `;
  box.classList.remove("hidden");
}

function refreshClinicalPatientSelect(patients) {
  const sel = $c("#clinical-patient-id");
  if (!sel) return;
  const current = sel.value;
  const list = patients || window.patientsCache || [];
  sel.innerHTML =
    '<option value="">— Selecciona un paciente —</option>' +
    list
      .map(
        (p) =>
          `<option value="${escapeHtml(p.patient_id)}">${escapeHtml(
            p.display_name || p.patient_id
          )}</option>`
      )
      .join("");
  if (current) sel.value = current;
}

window.refreshClinicalPatientSelect = refreshClinicalPatientSelect;

window.openClinicalForPatient = function (patient) {
  if (!patient) return;
  document.querySelector('[data-panel="clinical"]')?.click();
  const sel = $c("#clinical-patient-id");
  if (sel) sel.value = patient.patient_id;
};

$c("#clinical-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  showClinicalError(null);
  $c("#clinical-result")?.classList.add("hidden");

  const patientId = $c("#clinical-patient-id")?.value?.trim();
  const symptoms = $c("#clinical-symptoms")?.value?.trim();
  const ageRaw = $c("#clinical-age")?.value;
  const sex = $c("#clinical-sex")?.value?.trim();

  if (!patientId) {
    showClinicalError("Selecciona un paciente.");
    return;
  }
  if (!symptoms || symptoms.length < 3) {
    showClinicalError("Describe los síntomas (mínimo 3 caracteres).");
    return;
  }

  const body = { patient_id: patientId, symptoms };
  if (ageRaw !== "" && ageRaw != null) body.age = parseInt(ageRaw, 10);
  if (sex) body.sex = sex;

  const btn = $c("#clinical-submit");
  btn.disabled = true;
  btn.textContent = "Analizando…";

  try {
    const res = await fetch("/api/clinical/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || res.statusText);
    renderClinicalResult(data);
    if (window.loadPatients && patientId === window.getSelectedPatientId?.()) {
      await window.loadPatients();
    }
  } catch (err) {
    showClinicalError(err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Analizar síntomas";
  }
});

document.addEventListener("DOMContentLoaded", () => {
  if (window.patientsCache?.length) refreshClinicalPatientSelect(window.patientsCache);
});
