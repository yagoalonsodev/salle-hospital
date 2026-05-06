-- Centros hospitalarios (catálogo) y estudios clínicos sin ground truth ficticio

CREATE TABLE IF NOT EXISTS sites (
    site_code  VARCHAR(16) PRIMARY KEY,
    site_name  VARCHAR(80)  NOT NULL,
    active     BOOLEAN      NOT NULL DEFAULT TRUE
);

INSERT INTO sites (site_code, site_name) VALUES
    ('LSHC-01', 'laSalle Health Center')
ON CONFLICT (site_code) DO NOTHING;

DELETE FROM sites WHERE site_code = 'LSHC-API';

ALTER TYPE data_split ADD VALUE IF NOT EXISTS 'clinical';

ALTER TABLE studies ALTER COLUMN label DROP NOT NULL;

ALTER TABLE patients DROP CONSTRAINT IF EXISTS patients_site_code_fkey;
ALTER TABLE patients
    ADD CONSTRAINT patients_site_code_fkey
    FOREIGN KEY (site_code) REFERENCES sites (site_code);

ALTER TABLE patients ALTER COLUMN site_code DROP DEFAULT;
