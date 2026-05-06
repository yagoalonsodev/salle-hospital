-- Nombre visible en UI (dato real introducido al alta; sin autogenerar placeholders)
ALTER TABLE patients
    ADD COLUMN IF NOT EXISTS display_name VARCHAR(80);

-- Solo filas legacy sin nombre: se eliminan en 05-remove-demo-rows.sql si son de prueba
