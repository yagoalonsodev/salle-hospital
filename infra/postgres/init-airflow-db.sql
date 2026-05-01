-- Base de datos de metadatos para Apache Airflow (standalone)
CREATE USER airflow WITH PASSWORD 'airflow_secret';
CREATE DATABASE airflow OWNER airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
