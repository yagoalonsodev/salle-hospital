-- Esquema aplicación laSalle Health Center (BD salle_hospital)
-- Ver docs/database-architecture.md

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Tipos enumerados
CREATE TYPE study_label AS ENUM ('sana', 'neumonia', 'covid');
CREATE TYPE data_split AS ENUM ('train', 'val', 'test');
CREATE TYPE pipeline_status AS ENUM ('pending', 'running', 'ok', 'failed');
CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical');
CREATE TYPE quality_issue_type AS ENUM (
    'incomplete',
    'duplicate',
    'corrupt',
    'invalid_label',
    'other'
);

-- Pacientes (datos anonimizados/simulados)
CREATE TABLE patients (
    patient_id   VARCHAR(16)  PRIMARY KEY,
    sex          CHAR(1)      NOT NULL CHECK (sex IN ('M', 'F', 'X')),
    age_range    VARCHAR(10)  NOT NULL,
    site_code    VARCHAR(16)  NOT NULL DEFAULT 'LSHC-01',
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE patients IS 'Pacientes simulados; sin identificadores reales (RGPD simulado).';

-- Estudios de imagen (metadatos; binario en MinIO)
CREATE TABLE studies (
    study_id          VARCHAR(20)   PRIMARY KEY,
    patient_id        VARCHAR(16)   NOT NULL REFERENCES patients (patient_id) ON DELETE RESTRICT,
    file_path         TEXT          NOT NULL,
    minio_object_key  TEXT,
    split             data_split    NOT NULL,
    label             study_label   NOT NULL,
    source_dataset    VARCHAR(64)   NOT NULL,
    modality          VARCHAR(8)    NOT NULL DEFAULT 'CR',
    body_part         VARCHAR(32)   NOT NULL DEFAULT 'chest',
    captured_at       TIMESTAMPTZ   NOT NULL,
    ingested_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_studies_file_path UNIQUE (file_path)
);

COMMENT ON TABLE studies IS 'Metadatos de radiografías; object_key apunta a MinIO tras ingesta D2-04.';
COMMENT ON COLUMN studies.minio_object_key IS 'Ej: xray-images/raw/{study_id}.jpg';

CREATE INDEX idx_studies_patient_id ON studies (patient_id);
CREATE INDEX idx_studies_label ON studies (label);
CREATE INDEX idx_studies_split ON studies (split);
CREATE INDEX idx_studies_ingested_at ON studies (ingested_at DESC);

-- Predicciones del modelo TensorFlow
CREATE TABLE predictions (
    prediction_id    BIGSERIAL     PRIMARY KEY,
    study_id         VARCHAR(20)   NOT NULL REFERENCES studies (study_id) ON DELETE CASCADE,
    predicted_label  study_label   NOT NULL,
    prob_sana        NUMERIC(6, 5) NOT NULL CHECK (prob_sana >= 0 AND prob_sana <= 1),
    prob_neumonia    NUMERIC(6, 5) NOT NULL CHECK (prob_neumonia >= 0 AND prob_neumonia <= 1),
    prob_covid       NUMERIC(6, 5) NOT NULL CHECK (prob_covid >= 0 AND prob_covid <= 1),
    model_name       VARCHAR(64)   NOT NULL,
    model_version    VARCHAR(32)   NOT NULL,
    inferred_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_predictions_probs_sum CHECK (
        ABS((prob_sana + prob_neumonia + prob_covid) - 1.0) < 0.0001
    )
);

COMMENT ON TABLE predictions IS 'Salida del servicio ML; una fila por inferencia.';

CREATE INDEX idx_predictions_study_id ON predictions (study_id);
CREATE INDEX idx_predictions_inferred_at ON predictions (inferred_at DESC);
CREATE INDEX idx_predictions_predicted_label ON predictions (predicted_label);

-- Ejecuciones de jobs (Spark, ingesta, ML batch)
CREATE TABLE pipeline_runs (
    run_id           VARCHAR(32)     PRIMARY KEY,
    job_name         VARCHAR(64)     NOT NULL,
    stage            VARCHAR(32)     NOT NULL,
    status           pipeline_status NOT NULL DEFAULT 'pending',
    records_in       INTEGER         NOT NULL DEFAULT 0 CHECK (records_in >= 0),
    records_out      INTEGER         NOT NULL DEFAULT 0 CHECK (records_out >= 0),
    records_failed   INTEGER         NOT NULL DEFAULT 0 CHECK (records_failed >= 0),
    error_message    TEXT,
    started_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    finished_at      TIMESTAMPTZ,
    CONSTRAINT chk_pipeline_runs_finished CHECK (
        finished_at IS NULL OR finished_at >= started_at
    )
);

COMMENT ON TABLE pipeline_runs IS 'Cabecera de ejecución de pipeline (Airflow/Spark).';

CREATE INDEX idx_pipeline_runs_status ON pipeline_runs (status);
CREATE INDEX idx_pipeline_runs_started_at ON pipeline_runs (started_at DESC);

-- Eventos detallados por ejecución
CREATE TABLE pipeline_events (
    event_id    VARCHAR(16)     PRIMARY KEY,
    run_id      VARCHAR(32)     NOT NULL REFERENCES pipeline_runs (run_id) ON DELETE CASCADE,
    stage       VARCHAR(32)     NOT NULL,
    status      pipeline_status NOT NULL,
    records     INTEGER         NOT NULL DEFAULT 0 CHECK (records >= 0),
    message     TEXT,
    logged_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE pipeline_events IS 'Log operativo por etapa (ingesta, validación, ETL, inferencia).';

CREATE INDEX idx_pipeline_events_run_id ON pipeline_events (run_id);
CREATE INDEX idx_pipeline_events_logged_at ON pipeline_events (logged_at DESC);

-- Calidad de datos (Spark / validadores)
CREATE TABLE data_quality_issues (
    issue_id      BIGSERIAL          PRIMARY KEY,
    run_id        VARCHAR(32)        REFERENCES pipeline_runs (run_id) ON DELETE SET NULL,
    study_id      VARCHAR(20)        REFERENCES studies (study_id) ON DELETE SET NULL,
    issue_type    quality_issue_type NOT NULL,
    details       TEXT,
    detected_at   TIMESTAMPTZ        NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE data_quality_issues IS 'Registros incompletos, duplicados o corruptos detectados en ETL.';

CREATE INDEX idx_quality_issues_type ON data_quality_issues (issue_type);
CREATE INDEX idx_quality_issues_detected_at ON data_quality_issues (detected_at DESC);

-- Alertas para dashboard / operaciones
CREATE TABLE alerts (
    alert_id      BIGSERIAL       PRIMARY KEY,
    run_id        VARCHAR(32)     REFERENCES pipeline_runs (run_id) ON DELETE SET NULL,
    severity      alert_severity  NOT NULL DEFAULT 'info',
    title         VARCHAR(128)    NOT NULL,
    message       TEXT            NOT NULL,
    acknowledged  BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE alerts IS 'Notificaciones simuladas (fallos pipeline, umbrales calidad, etc.).';

CREATE INDEX idx_alerts_severity ON alerts (severity);
CREATE INDEX idx_alerts_created_at ON alerts (created_at DESC);
CREATE INDEX idx_alerts_ack ON alerts (acknowledged) WHERE NOT acknowledged;

-- Vistas de apoyo (dashboard / API)
CREATE OR REPLACE VIEW v_study_counts_by_label AS
SELECT
    label,
    split,
    COUNT(*) AS study_count
FROM studies
GROUP BY label, split
ORDER BY label, split;

CREATE OR REPLACE VIEW v_prediction_summary AS
SELECT
    p.predicted_label,
    COUNT(*) AS total,
    ROUND(AVG(p.prob_sana)::numeric, 4)    AS avg_prob_sana,
    ROUND(AVG(p.prob_neumonia)::numeric, 4) AS avg_prob_neumonia,
    ROUND(AVG(p.prob_covid)::numeric, 4)   AS avg_prob_covid
FROM predictions p
GROUP BY p.predicted_label;
