#!/usr/bin/env bash
# Entrena candidatos pendientes (sin ResNet50) y genera architecture_comparison.json
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv-metal/bin/activate
export FEATURES_ROOT="${FEATURES_ROOT:-$(cd .. && pwd)/data/processed/features}"
export FEATURES_VERSION=v1 TRAIN_BATCH_SIZE=16 HEAD_EPOCHS=8 FINETUNE_EPOCHS=6 EXPORT_SAVEDMODEL=0

LOG_DIR=models/reports
mkdir -p "$LOG_DIR"

run_if_needed() {
  local script=$1
  local name=$2
  echo "=== $name ==="
  python -u "scripts/$script"
}

if [[ ! -f models/reports/rx_baseline_cnn_v1/training_report.json ]]; then
  run_if_needed train_baseline_cnn.py baseline_cnn
fi
run_if_needed train_efficientnetb0.py efficientnetb0
run_if_needed train_densenet121.py densenet121

COMPARE_ARCHS=baseline_cnn,resnet50,efficientnetb0,densenet121 AGGREGATE_ONLY=1 \
  python -u scripts/train_compare_architectures.py

echo "Listo: models/reports/architecture_comparison.json"
