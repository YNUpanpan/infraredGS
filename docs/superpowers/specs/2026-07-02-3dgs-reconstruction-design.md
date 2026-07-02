# 3DGS Visible and Thermal UAV Reconstruction Design

## Context

The dataset contains 339 visible-light UAV images and 339 thermal UAV images captured during an orbit flight. The local workspace currently contains paired DJI-style filenames such as `*_V.JPG` and `*_T.JPG`, plus a timestamp `.MRK` file. The target compute environment is an RTX 5090 server running Ubuntu 22.04, but this phase does not connect to or operate that server.

The project will become a reproducible experiment repository. Git will track documentation, scripts, configs, manifests, and logs. Raw images, COLMAP work products, model checkpoints, Gaussian outputs, and other heavy artifacts will stay outside Git.

## Goals

- Build a lightweight local repository structure for reproducible 3DGS experiments.
- Record all task decisions and actions in `AGENT.md`.
- Prepare a workflow that first runs independent visible and thermal reconstructions, then attempts visible-geometry plus thermal-registration fusion.
- Prepare Ubuntu 22.04 plus RTX 5090 server instructions and script templates without assuming the server environment has already been configured.
- Keep all raw UAV image files out of GitHub.

## Non-Goals

- Do not upload the 678 raw images to GitHub.
- Do not directly operate the RTX 5090 server in this phase.
- Do not build a fully automated one-command pipeline before the actual server environment is inspected.
- Do not batch-delete files or directories.

## Repository Design

The repository should be organized as a reproducible experiment project:

```text
project/
  AGENT.md
  README.md
  .gitignore
  docs/
    server-runbook.md
    reconstruction-design.md
    fusion-plan.md
    github-publish.md
  scripts/
    prepare_dataset.py
    run_colmap_visible.sh
    run_colmap_thermal.sh
    train_3dgs_visible.sh
    train_3dgs_thermal.sh
    archive_results.sh
  configs/
    dataset.example.yaml
    gaussian-splatting.example.yaml
  manifests/
    dataset_manifest.csv
```

Raw data may remain in the current directory initially or later move to a local/server data directory. Git ignore rules must exclude raw images and generated artifacts, including `*.JPG`, `data/raw/`, `work/`, `outputs/`, `*.ply`, checkpoints, COLMAP databases, and model binaries.

## Data Manifest

`scripts/prepare_dataset.py` will inspect visible and thermal filenames, pair records by sequence number, and write `manifests/dataset_manifest.csv`. The manifest should include at least:

- sequence id
- visible filename
- thermal filename
- visible exists
- thermal exists
- notes

The current dataset appears to contain 339 visible files and 339 thermal files. The design assumes same-sequence filenames such as `0400_V.JPG` and `0400_T.JPG` represent paired captures, but the manifest step will verify this explicitly.

## B Stage: Independent Reconstructions

The first reconstruction stage runs visible and thermal workflows independently:

```text
data/raw/
  visible/
  thermal/

work/
  colmap_visible/
  colmap_thermal/

outputs/
  3dgs_visible/
  3dgs_thermal/
  reports/
```

The visible workflow:

1. Use visible images as COLMAP input.
2. Generate camera poses, sparse reconstruction, and 3DGS-compatible input.
3. Train a visible 3DGS model.
4. Archive logs, commands, key parameters, and visual quality notes.

The thermal workflow:

1. Use thermal images as COLMAP input.
2. Attempt independent camera pose estimation and sparse reconstruction.
3. Train a thermal 3DGS model if COLMAP output is usable.
4. Document thermal-specific failure modes such as low texture, repeated regions, or weak matching.

The B stage success criteria are two comparable baselines: a stable visible model when possible, and a documented thermal model or failure analysis.

## C Stage: Visible Geometry Plus Thermal Fusion

The C stage depends on B-stage results. It should not replace the independent baselines. It creates a third experiment track:

```text
work/
  fusion/
    pair_map.csv
    visible_colmap_reference/
    thermal_registered/
    transforms/
    diagnostics/

outputs/
  fusion_visible_geometry_thermal_view/
  reports/fusion_report.md
```

The fusion workflow:

1. Confirm visible/thermal image pairing through the manifest.
2. Use visible COLMAP poses and sparse geometry as the stable reference.
3. Bind thermal images to visible poses by sequence number if the two sensors are sufficiently aligned.
4. If direct binding is not accurate enough, add a calibration, affine, homography, or other registration step.
5. Produce diagnostics that show whether thermal views align with visible geometry.
6. Record fusion assumptions, failed examples, and required calibration work in `fusion_report.md`.

## Server Runbook Scope

`docs/server-runbook.md` will cover:

- Ubuntu 22.04 system checks: GPU, driver, CUDA, disk, conda, git, compilers.
- Recommended project, dataset, and experiment directories on the server.
- COLMAP installation or build strategy.
- PyTorch/CUDA and 3DGS dependency strategy for RTX 5090.
- Data transfer expectations, with raw images stored outside the Git repository.
- B-stage visible and thermal execution commands.
- C-stage fusion preparation and diagnostics.
- Result archiving and experiment note format.

Because RTX 5090 support may require newer CUDA and PyTorch builds, the runbook must instruct the operator to verify `nvidia-smi`, driver version, CUDA version, and PyTorch CUDA compatibility on the actual server before finalizing commands.

## Git and GitHub Workflow

The initial repository will be local-only. GitHub remote configuration happens later after ignore rules and repository structure are confirmed.

The later publish workflow will:

1. Check `git status`.
2. Confirm no raw images, checkpoints, COLMAP outputs, or model files are staged.
3. Add the GitHub remote.
4. Push the local repository.
5. Continue committing `AGENT.md` updates after each task.

## Safety Constraints

- Do not use bulk deletion commands such as `rm -rf`, `del /s`, `rd /s`, `rmdir /s`, or recursive `Remove-Item`.
- If cleanup of many files is needed, stop and ask the user to handle it manually.
- Delete only one explicit file path at a time when deletion is unavoidable and approved.
- Keep raw images out of version control.

## Open Implementation Items

- Create `.gitignore`, `README.md`, docs, configs, manifests, and scripts after this design is reviewed.
- Decide whether `prepare_dataset.py` should copy, move, or only inventory files. The safest default is inventory-only, with explicit user approval before any file moves.
- Inspect the actual RTX 5090 server environment before finalizing CUDA/PyTorch install commands.
