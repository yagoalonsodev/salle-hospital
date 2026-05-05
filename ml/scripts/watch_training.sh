#!/usr/bin/env bash
# Seguimiento del entrenamiento comparativo (ejecutar en una terminal aparte)
LOG="${1:-$(dirname "$0")/../models/reports/train_all_compare.log}"
REPORTS="$(dirname "$0")/../models/reports"

echo "═══════════════════════════════════════════════════════════"
echo "  Monitor entrenamiento — laSalle ML"
echo "  Log: $LOG"
echo "  Ctrl+C para salir"
echo "═══════════════════════════════════════════════════════════"
echo ""

while true; do
  clear
  echo "═══ $(date '+%H:%M:%S') ═══"
  echo ""
  if pgrep -fl "train_baseline|train_efficient|train_densenet|train_compare" >/dev/null 2>&1; then
    echo "Estado: ENTRENANDO"
    pgrep -fl "train_baseline|train_efficient|train_densenet|train_compare" 2>/dev/null | head -3
  else
    echo "Estado: sin proceso train_* (¿terminado?)"
  fi
  echo ""
  echo "Informes generados:"
  for arch in baseline_cnn resnet50 efficientnetb0 densenet121; do
  case $arch in
    resnet50) f="$REPORTS/training_report_v1.json" ;;
    *) f="$REPORTS/rx_${arch}_v1/training_report.json" ;;
  esac
    if [[ -f "$f" ]]; then echo "  ✓ $arch"; else echo "  · $arch (pendiente)"; fi
  done
  echo ""
  echo "─── Últimas líneas del log ───"
  tail -8 "$LOG" 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g' | tr '\r' '\n' | grep -E "^(===|Epoch |.*TEST |Listo|Ranking|Ganador)" | tail -6
  echo ""
  echo "─── Último progreso de época ───"
  tail -1 "$LOG" 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g' | tr '\r' '\n' | tail -1
  sleep 30
done
