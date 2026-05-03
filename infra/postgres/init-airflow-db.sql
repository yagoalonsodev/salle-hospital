-- Base de datos de metadatos para Apache Airflow (standalone)
-- PASSWORD debe coincidir con AIRFLOW_DB_PASSWORD en .env (ver .env.example)
CREATE USER airflow WITH PASSWORD 'airflow_secret';
CREATE DATABASE airflow OWNER airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
