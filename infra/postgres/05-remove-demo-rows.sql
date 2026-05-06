-- Elimina filas de prueba creadas en desarrollo (nombres «Paciente PAT-…», uploads de test)
DELETE FROM predictions
WHERE study_id IN (SELECT study_id FROM studies WHERE source_dataset = 'api_upload');

DELETE FROM studies WHERE source_dataset = 'api_upload';

-- Pacientes de prueba (nombre autogenerado o sin estudios reales de ingesta)
DELETE FROM patients p
WHERE p.display_name LIKE 'Paciente %'
   OR (
       NOT EXISTS (SELECT 1 FROM studies s WHERE s.patient_id = p.patient_id)
       AND p.site_code IN ('LSHC-API', 'LSHC-01')
   );
