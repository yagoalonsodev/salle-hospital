// Inicialización BD de logs (usuario root = MONGO_INITDB_ROOT_* en compose, mismo patrón que Postgres en .env)
db = db.getSiblingDB("salle_logs");

db.createCollection("application_logs");
db.createCollection("airflow_logs");
db.createCollection("file_logs");
db.createCollection("log_sync_cursors");

db.application_logs.createIndex({ timestamp: -1 });
db.application_logs.createIndex({ service: 1, timestamp: -1 });
db.application_logs.createIndex({ level: 1 });

db.airflow_logs.createIndex({ timestamp: -1 });
db.airflow_logs.createIndex({ dag_id: 1, task_id: 1 });

db.file_logs.createIndex({ timestamp: -1 });
db.file_logs.createIndex({ path: 1 });
