#!/usr/bin/env bash
set -euo pipefail

DATASET_ROOT="${DATASET_ROOT:-$HOME/datasets/uav_3dgs}"
EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-$HOME/experiments/uav_3dgs}"
IMAGE_DIR="$DATASET_ROOT/raw/thermal"
WORK_DIR="$EXPERIMENT_ROOT/colmap_thermal"

mkdir -p "$WORK_DIR/sparse" "$WORK_DIR/dense"

colmap feature_extractor \
  --database_path "$WORK_DIR/database.db" \
  --image_path "$IMAGE_DIR" \
  --ImageReader.single_camera 1

colmap exhaustive_matcher \
  --database_path "$WORK_DIR/database.db"

colmap mapper \
  --database_path "$WORK_DIR/database.db" \
  --image_path "$IMAGE_DIR" \
  --output_path "$WORK_DIR/sparse"
