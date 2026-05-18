#!/usr/bin/env bash
# Verificación integral del stack laSalle Health Center.
# No entrena modelos ML; comprueba infra, datos, API, dashboard y pipeline.
#
# Uso (desde la raíz del repo):
#   ./scripts/verify_stack.sh
#   SKIP_COMPOSE_UP=1 ./scripts/verify_stack.sh
#   VERIFY_LOG=logs/verify_stack.log ./scripts/verify_stack.sh
#
# Requiere: Docker, docker compose, curl, python3, .env

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# No usar set -e: queremos ejecutar TODAS las pruebas y resumir al final
set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

declare -a RESULT_LABELS=()
declare -a RESULT_STATUS=()
declare -a RESULT_DETAIL=()

failures=0
warnings=0
passed=0

LOG_FILE="${VERIFY_LOG:-}"
if [[ -n "$LOG_FILE" ]]; then
  mkdir -p "$(dirname "$LOG_FILE")"
  exec > >(tee -a "$LOG_FILE") 2>&1
  echo "=== Log: $LOG_FILE — $(date -Iseconds) ==="
fi

log() { echo -e "[$(date +%H:%M:%S)] $*"; }

record() {
  local label="$1" status="$2" detail="${3:-}"
  RESULT_LABELS+=("$label")
  RESULT_STATUS+=("$status")
  RESULT_DETAIL+=("$detail")
  case "$status" in
    OK) passed=$((passed + 1)) ;;
    WARN) warnings=$((warnings + 1)) ;;
    FAIL) failures=$((failures + 1)) ;;
  esac
}

pass() {
  log "${GREEN}OK${NC}   $*"
  record "$1" OK "${*:2}"
}

warn() {
  log "${YELLOW}WARN${NC} $*"
  record "$1" WARN "${*:2}"
}

fail() {
  log "${RED}FAIL${NC} $*"
  record "$1" FAIL "${*:2}"
}

info() { log "${CYAN}INFO${NC} $*"; }

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
else
  warn "Entorno" "No hay .env; valores por defecto de docker-compose"
fi

API_CHECK="${VERIFY_API_URL:-http://localhost:8000}"
ML_CHECK="${VERIFY_ML_URL:-http://localhost:8001}"
DASH_CHECK="${VERIFY_DASH_URL:-http://localhost:8501}"
AIRFLOW_CHECK="${VERIFY_AIRFLOW_URL:-http://localhost:8081}"
SPARK_UI_CHECK="${VERIFY_SPARK_UI_URL:-http://localhost:8080}"
MINIO_CONSOLE_CHECK="${VERIFY_MINIO_CONSOLE_URL:-http://localhost:9001}"

POSTGRES_USER="${POSTGRES_USER:-salle}"
POSTGRES_DB="${POSTGRES_DB:-salle_hospital}"
COMPOSE="docker compose"
AIRFLOW_WAIT_SEC="${VERIFY_AIRFLOW_WAIT:-300}"

section() {
  echo ""
  echo -e "${BOLD}========== $* ==========${NC}"
}

wait_healthy() {
  local name="$1"
  local max="${2:-120}"
  local mode="${3:-strict}" # strict | lenient (lenient: timeout -> warn, no FAIL)
  local i=0
  local status="unknown"
  info "Esperando healthcheck de $name (máx ${max}s, modo=$mode)..."
  while (( i < max )); do
    status="$(docker inspect -f '{{.State.Health.Status}}' "$name" 2>/dev/null || echo "none")"
    if [[ "$status" == "healthy" ]]; then
      pass "$name healthcheck" "healthy tras ${i}s"
      return 0
    fi
    if [[ "$status" == "none" ]]; then
      local running
      running="$(docker inspect -f '{{.State.Running}}' "$name" 2>/dev/null || echo "false")"
      if [[ "$running" == "true" ]]; then
        pass "$name healthcheck" "en ejecución (sin healthcheck Docker)"
        return 0
      fi
    fi
    if (( i > 0 && i % 20 == 0 )); then
      info "  … $name sigue en '$status' (${i}s)"
    fi
    sleep 2
    i=$((i + 2))
  done
  local tail_log
  tail_log="$(docker logs --tail 8 "$name" 2>&1 | sed 's/^/    | /')"
  if [[ "$mode" == "lenient" ]]; then
    warn "$name healthcheck (Docker)" "timeout ${max}s, estado=$status — el servicio puede estar operativo (ver scheduler/UI). Log:${tail_log}"
    return 1
  fi
  fail "$name healthcheck" "timeout ${max}s, último estado=$status. Últimas líneas log:${tail_log}"
  return 1
}

http_check() {
  local label="$1" url="$2"
  local expect_re="${3:-^(200|204)$}"
  local code body err_file
  err_file="$(mktemp)"
  code="$(curl -sS -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 20 "$url" 2>"$err_file" || echo "000")"
  if [[ "$code" =~ $expect_re ]]; then
    pass "$label" "HTTP $code — $url"
    rm -f "$err_file"
    return 0
  fi
  local err
  err="$(tr '\n' ' ' <"$err_file" | head -c 120)"
  rm -f "$err_file"
  fail "$label" "HTTP $code — $url ${err:+($err)}"
  return 1
}

json_health_api() {
  local url="$API_CHECK/health"
  local body err
  body="$(curl -sf --connect-timeout 5 --max-time 20 "$url" 2>&1)" || {
    fail "API /health" "sin respuesta: $body"
    return 1
  }
  info "API /health JSON: $(echo "$body" | python3 -c "import json,sys; d=json.load(sys.stdin); print({k:d['checks'][k]['ok'] for k in d.get('checks',{})}, 'status=', d.get('status'))" 2>/dev/null || echo "$body" | head -c 120)"
  if echo "$body" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='ok' and all(d['checks'][k]['ok'] for k in d['checks']) else 1)" 2>/dev/null; then
    pass "API /health (DB+MinIO+ML)" "status=ok, todos los checks true"
    return 0
  fi
  fail "API /health (DB+MinIO+ML)" "$(echo "$body" | head -c 300)"
  return 1
}

json_health_ml() {
  local url="$ML_CHECK/health"
  local body
  body="$(curl -sf --connect-timeout 5 --max-time 30 "$url" 2>&1)" || {
    fail "ML /health" "sin respuesta (¿modelo aún cargando?): $body"
    return 1
  }
  info "ML /health: $(echo "$body" | python3 -c "import json,sys; d=json.load(sys.stdin); print('loaded=',d.get('model_loaded'),'version=',d.get('model_version'))" 2>/dev/null || echo "$body" | head -c 120)"
  if echo "$body" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='ok' and d.get('model_loaded') else 1)" 2>/dev/null; then
    pass "ML /health (modelo cargado)" "$(echo "$body" | python3 -c "import json,sys; print(json.load(sys.stdin).get('model_version','?'))" 2>/dev/null)"
    return 0
  fi
  fail "ML /health" "$(echo "$body" | head -c 300)"
  return 1
}

http_code_only() {
  curl -sS -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 25 "$1" 2>/dev/null || echo "000"
}

print_summary_table() {
  section "RESUMEN — qué funciona y qué no"
  printf "${BOLD}%-42s %-6s %s${NC}\n" "PRUEBA" "ESTADO" "DETALLE"
  printf '%s\n' "$(printf '─%.0s' {1..90})"
  local i
  for i in "${!RESULT_LABELS[@]}"; do
    local st="${RESULT_STATUS[$i]}"
    local color="$NC"
    [[ "$st" == OK ]] && color="$GREEN"
    [[ "$st" == FAIL ]] && color="$RED"
    [[ "$st" == WARN ]] && color="$YELLOW"
    printf "${color}%-42s %-6s${NC} %s\n" "${RESULT_LABELS[$i]}" "$st" "${RESULT_DETAIL[$i]:--}"
  done
  echo ""
  echo -e "${BOLD}Totales:${NC} ${GREEN}OK=$passed${NC}  ${YELLOW}WARN=$warnings${NC}  ${RED}FAIL=$failures${NC}"
}

section "1. Arranque (enunciado: docker compose up -d --build)"
START_TS=$(date +%s)
if [[ "${SKIP_COMPOSE_UP:-0}" != "1" ]]; then
  info "Ejecutando: $COMPOSE up -d --build"
  if $COMPOSE up -d --build; then
    pass "docker compose up" "build + start completado"
  else
    fail "docker compose up" "comando falló (ver salida arriba)"
  fi
else
  warn "docker compose up" "SKIP_COMPOSE_UP=1 — stack no relanzado"
fi

section "2. Contenedores esperados"
EXPECTED=(
  salle-postgres salle-minio salle-api salle-ml salle-dashboard
  salle-spark-master salle-spark-worker salle-pipeline salle-airflow salle-watcher
)
for c in "${EXPECTED[@]}"; do
  if docker ps --format '{{.Names}}' | grep -qx "$c"; then
    cst="$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null)"
    if [[ "$c" == "salle-watcher" ]] && docker ps --filter name=salle-watcher --format '{{.Status}}' | grep -qi restarting; then
      wlog="$(docker logs --tail 5 salle-watcher 2>&1 | tr '\n' ' ' | head -c 200)"
      fail "Contenedor $c" "restarting — $wlog"
    else
      pass "Contenedor $c" "running ($cst)"
    fi
  else
    fail "Contenedor $c" "no aparece en docker ps"
  fi
done

section "3. Healthchecks Docker"
wait_healthy salle-postgres 120 || true
wait_healthy salle-api 150 || true
wait_healthy salle-ml 240 || true
wait_healthy salle-dashboard 150 || true
# Airflow standalone: el healthcheck Docker a veces queda unhealthy aunque el scheduler funcione
wait_healthy salle-airflow "$AIRFLOW_WAIT_SEC" lenient || true

# Airflow: scheduler/DAG pueden estar bien aunque el healthcheck Docker falle
AF_SCHED_OK=0
if docker exec salle-airflow airflow jobs check --job-type SchedulerJob >/dev/null 2>&1; then
  AF_SCHED_OK=1
  pass "Airflow scheduler" "SchedulerJob activo"
else
  fail "Airflow scheduler" "SchedulerJob no responde"
fi

section "4. HTTP — API, ML, dashboard, Airflow, Spark, MinIO"
json_health_api || true
json_health_ml || true
http_check "Dashboard Streamlit" "$DASH_CHECK/_stcore/health" || true
# UI webserver puede tardar o reiniciar; no duplicar FAIL+WARN
af_ui_code="000"
n=1
while (( n <= 12 )); do
  af_ui_code="$(http_code_only "$AIRFLOW_CHECK/health")"
  if [[ "$af_ui_code" =~ ^(200|204)$ ]]; then
    pass "Airflow UI /health" "HTTP $af_ui_code — $AIRFLOW_CHECK/health (intento $n/12)"
    break
  fi
  info "  Airflow UI intento $n/12 → HTTP $af_ui_code; espera 10s..."
  sleep 10
  n=$((n + 1))
done
if [[ ! "$af_ui_code" =~ ^(200|204)$ ]]; then
  if [[ "$AF_SCHED_OK" -eq 1 ]]; then
    warn "Airflow UI /health" "sin HTTP estable en :8081 (último=$af_ui_code); scheduler OK — prueba: docker compose restart airflow"
  else
    fail "Airflow UI /health" "HTTP $af_ui_code y scheduler no verificado"
  fi
fi
http_check "Spark Master UI" "$SPARK_UI_CHECK" || true
http_check "MinIO consola" "$MINIO_CONSOLE_CHECK" || true

section "5. API — datos clínicos y dashboard"
http_check "GET /api/patients" "$API_CHECK/api/patients?limit=1" || true
http_check "GET /api/dashboard" "$API_CHECK/api/dashboard" || true

section "6. PostgreSQL — tablas núcleo"
if docker exec salle-postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; then
  pass "PostgreSQL pg_isready" "$POSTGRES_DB@$POSTGRES_USER"
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    n="${line#*:}"
    key="${line%%:*}"
    if [[ "${n:-0}" -gt 0 ]]; then
      pass "Postgres $key" "count=$n"
    else
      fail "Postgres $key" "tabla vacía (¿ingesta CSV/imágenes?)"
    fi
  done < <(docker exec salle-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c \
    "SELECT 'patients'||':'||COUNT(*) FROM patients
     UNION ALL SELECT 'studies'||':'||COUNT(*) FROM studies
     UNION ALL SELECT 'pipeline_runs_ok'||':'||COUNT(*) FROM pipeline_runs WHERE status='ok'
     UNION ALL SELECT 'predictions'||':'||COUNT(*) FROM predictions;")
else
  fail "PostgreSQL" "pg_isready falló en salle-postgres"
fi

section "7. Pipeline — MinIO + informe ingesta"
PIPE_LOG="$(mktemp)"
if docker exec salle-pipeline python3 /opt/scripts/verify_pipeline_integration.py >"$PIPE_LOG" 2>&1; then
  pass "verify_pipeline_integration.py" "$(grep -E '^OK ' "$PIPE_LOG" | tr '\n' '; ' | head -c 200)"
  cat "$PIPE_LOG" | sed 's/^/  | /'
else
  fail "verify_pipeline_integration.py" "ver salida abajo"
  cat "$PIPE_LOG" | sed 's/^/  | /'
fi
rm -f "$PIPE_LOG"

section "8. Airflow — DAG salle_rx_pipeline"
AF_LOG="$(mktemp)"
if docker exec salle-airflow airflow dags list >"$AF_LOG" 2>&1; then
  if grep -q salle_rx_pipeline "$AF_LOG"; then
    pass "DAG salle_rx_pipeline" "$(grep salle_rx_pipeline "$AF_LOG" | head -1 | tr -s ' ')"
  else
    fail "DAG salle_rx_pipeline" "no listado; salida: $(head -5 "$AF_LOG" | tr '\n' ' ')"
  fi
else
  fail "DAG salle_rx_pipeline" "airflow CLI error: $(head -3 "$AF_LOG" | tr '\n' ' ')"
fi
rm -f "$AF_LOG"

section "9. Spark — submit smoke test"
SPARK_LOG="$(mktemp)"
if docker exec salle-pipeline /opt/spark/bin/spark-submit \
  --master "${SPARK_MASTER_URL:-spark://spark-master:7077}" \
  /opt/scripts/spark_smoke_test.py >"$SPARK_LOG" 2>&1; then
  if grep -q SPARK_OK "$SPARK_LOG"; then
    pass "Spark submit smoke" "$(grep SPARK_OK "$SPARK_LOG" | tail -1 | tr -d '\r')"
  else
    fail "Spark submit smoke" "sin SPARK_OK en salida"
    tail -15 "$SPARK_LOG" | sed 's/^/  | /'
  fi
else
  fail "Spark submit smoke" "spark-submit exit != 0"
  tail -20 "$SPARK_LOG" | sed 's/^/  | /'
fi
rm -f "$SPARK_LOG"

section "10. CSV clínico (D2-03)"
if docker exec salle-pipeline test -f /opt/data/raw/clinical/studies.csv 2>/dev/null; then
  rows="$(docker exec salle-pipeline wc -l /opt/data/raw/clinical/studies.csv | awk '{print $1}')"
  if [[ "${rows:-0}" -gt 1 ]]; then
    pass "studies.csv" "$((rows - 1)) filas de datos"
  else
    warn "studies.csv" "vacío; python3 scripts/build_clinical_data.py"
  fi
else
  warn "studies.csv" "no encontrado en /opt/data/raw/clinical/"
fi

section "11. URLs útiles (demo)"
info "UI hospital:    $API_CHECK"
info "Dashboard:      $DASH_CHECK"
info "Airflow:        $AIRFLOW_CHECK  (user en .env AIRFLOW_ADMIN_*)"
info "MinIO consola:  $MINIO_CONSOLE_CHECK"
info "Spark UI:       $SPARK_UI_CHECK"

END_TS=$(date +%s)
DURATION=$((END_TS - START_TS))

print_summary_table

echo ""
if [[ "$failures" -eq 0 ]]; then
  echo -e "${GREEN}${BOLD}=== VERIFICACIÓN COMPLETA OK ===${NC} (${DURATION}s)"
  echo "Stack operativo. Pendiente entregable: presentación Día 10."
  [[ -n "$LOG_FILE" ]] && echo "Log guardado en: $LOG_FILE"
  exit 0
fi

echo -e "${RED}${BOLD}=== VERIFICACIÓN CON $failures FALLO(S) ===${NC} (${DURATION}s, WARN=$warnings, OK=$passed)"
echo "Sugerencias:"
echo "  • Airflow lento tras rebuild: SKIP_COMPOSE_UP=1 ./scripts/verify_stack.sh"
echo "  • O más espera: VERIFY_AIRFLOW_WAIT=420 ./scripts/verify_stack.sh"
echo "  • Logs: docker compose logs airflow --tail 50"
[[ -n "$LOG_FILE" ]] && echo "Log completo: $LOG_FILE"
exit 1
