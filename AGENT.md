# Agent Work Log

## 2026-07-02 Session 001

### User Request
- Plan a 3D Gaussian Splatting reconstruction workflow for 339 visible UAV images and 339 thermal UAV images.
- Use a future RTX 5090 Ubuntu 22.04 server, but do not connect to or operate the server yet.
- Record every conversation task in `AGENT.md`.
- Eventually upload the project to GitHub, while keeping raw images out of the repository.

### Confirmed Decisions
- GitHub will track documentation, scripts, configs, manifests, and logs only. Raw images will not be uploaded.
- Reconstruction order: first run independent visible and thermal 3DGS workflows, then attempt visible-geometry plus thermal-registration fusion.
- Initial deliverable: a reproducible local experiment repository design plus server runbook and script templates.
- Server mode for now: prepare local repo and reproducible documentation only; do not directly operate the RTX 5090 server yet.
- GitHub mode for now: initialize a local git repository first; configure a remote later.
- Preferred repository style: reproducible experiment repository rather than a minimal notes repo or fully automated pipeline.

### Actions Taken
- Inspected the working directory and confirmed it contains 339 `*_V.JPG` visible images and 339 `*_T.JPG` thermal images.
- Confirmed the working directory was not yet a git repository.
- Confirmed no existing `AGENT.md` or `AGENTS.md` file was present in the workspace.
- Drafted and confirmed the high-level design in five sections:
  - Repository and data boundary.
  - Independent visible/thermal reconstruction workflow.
  - Later visible-geometry plus thermal-registration fusion workflow.
  - `AGENT.md`, local git, and later GitHub publishing workflow.
  - RTX 5090 Ubuntu 22.04 server runbook and script-template scope.

### Next Steps
- Write the approved design spec under `docs/superpowers/specs/`.
- Commit the design spec and this work log to local git.
- Ask the user to review the written spec before moving to the implementation plan.
