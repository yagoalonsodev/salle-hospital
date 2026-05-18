-- Dataset clínico textual (síntomas → diagnóstico), separado de radiografías

CREATE TYPE clinical_diagnosis AS ENUM (
    'sana',
    'neumonia',
    'covid',
    'gripe',
    'asma',
    'bronquitis',
    'epoc',
    'rinitis_alergica'
);

-- Registros importados del CSV 100k (ground truth para entrenamiento / auditoría)
CREATE TABLE clinical_records (
    record_id       VARCHAR(24) PRIMARY KEY,
    patient_ref     VARCHAR(24) NOT NULL,
    display_name    VARCHAR(80) NOT NULL,
    age             SMALLINT    NOT NULL CHECK (age >= 0 AND age <= 120),
    sex             CHAR(1)     NOT NULL CHECK (sex IN ('M', 'F', 'X')),
    symptoms        TEXT        NOT NULL,
    diagnosis       clinical_diagnosis NOT NULL,
    source_dataset  VARCHAR(64) NOT NULL DEFAULT 'clinical_records_100k',
    recorded_at     TIMESTAMPTZ NOT NULL,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clinical_records_diagnosis ON clinical_records (diagnosis);
CREATE INDEX idx_clinical_records_patient_ref ON clinical_records (patient_ref);

COMMENT ON TABLE clinical_records IS 'Dataset simulado 100k: síntomas y diagnóstico; independiente de studies (RX).';

-- Predicciones del modelo por síntomas (consultas API o batch)
CREATE TABLE clinical_predictions (
    prediction_id       BIGSERIAL PRIMARY KEY,
    patient_id          VARCHAR(16) NOT NULL REFERENCES patients (patient_id) ON DELETE CASCADE,
    record_id           VARCHAR(24) REFERENCES clinical_records (record_id) ON DELETE SET NULL,
    symptoms            TEXT        NOT NULL,
    age                 SMALLINT    CHECK (age IS NULL OR (age >= 0 AND age <= 120)),
    sex                 CHAR(1)     CHECK (sex IS NULL OR sex IN ('M', 'F', 'X')),
    predicted_diagnosis clinical_diagnosis NOT NULL,
    prob_json           JSONB       NOT NULL DEFAULT '{}',
    model_name          VARCHAR(64) NOT NULL,
    model_version       VARCHAR(32) NOT NULL,
    inferred_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clinical_predictions_patient ON clinical_predictions (patient_id);
CREATE INDEX idx_clinical_predictions_inferred ON clinical_predictions (inferred_at DESC);

COMMENT ON TABLE clinical_predictions IS 'Salida modelo síntomas (sklearn); distinto de predictions (RX ResNet50).';
