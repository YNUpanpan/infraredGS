#!/usr/bin/env bash
set -euo pipefail

GAUSSIAN_REPO="${GAUSSIAN_REPO:-$HOME/src/gaussian-splatting}"
EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-$HOME/experiments/uav_3dgs}"

python "$GAUSSIAN_REPO/train.py" \
  -s "$EXPERIMENT_ROOT/colmap_visible" \
  -m "$EXPERIMENT_ROOT/outputs/3dgs_visible" \
  --iterations "${ITERATIONS:-30000}"
