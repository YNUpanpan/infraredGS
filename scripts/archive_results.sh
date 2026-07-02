#!/usr/bin/env bash
set -euo pipefail

EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-$HOME/experiments/uav_3dgs}"
REPORT_DIR="$EXPERIMENT_ROOT/outputs/reports"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$REPORT_DIR/run_$STAMP.md"

mkdir -p "$REPORT_DIR"

{
  echo "# 实验记录 $STAMP"
  echo
  echo "## 环境"
  nvidia-smi || true
  echo
  echo "## 输出目录"
  find "$EXPERIMENT_ROOT/outputs" -maxdepth 2 -type d | sort
} > "$REPORT"

echo "$REPORT"
