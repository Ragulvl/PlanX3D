# FloorplanToBlender3D — Full Project Audit
**Date:** April 16, 2026  
**Scope:** A to Z — Architecture, Code Quality, Dependencies, Security, Testing, and Recommendations

---

## 1. Project Overview

FloorplanToBlender3D converts 2D architectural floorplan images into 3D Blender models using computer vision (OpenCV) and geometry generation. It supports three interfaces:

| Interface | Entry Point | Description |
|-----------|-------------|-------------|
| CLI | `cli_pipeline.py` | Interactive terminal pipeline |
| GUI | `gui_converter.py` | PySide6 desktop application |
| Server | `Server/main.py` | Flask REST API |

Output formats: `.blend`, `.obj`, `.fbx`, `.gltf`, `.x3d`

---

## 2. Project Structure

```
/
├── Blender/                    # Blender Python scripts (run inside Blender)
├── Configs/                    # INI configuration files
├── Data/                       # Generated geometry data (verts/faces JSON)
├── Development Center/         # R&D scripts, not part of production pipeline
├── FloorplanToBlenderLib/      # Core library (16 modules)
├── gui/                        # GUI components (PySide6)
├── Images/                     # Example images, logos, calibration assets
├── Server/                     # Flask REST API + Swagger
├── cli_pipeline.py             # CLI entry point
├── gui_converter.py            # GUI entry point
├── requirements_core.txt       # Core dependencies
├── requirements_gui.txt        # GUI dependencies
├── Configs/default.ini         # Per-floorplan config
└── Configs/system.ini          # System-level config (Blender path, format)
```

---

## 3. Dependencies Audit

### 3.1 Core (`requirements_core.txt`)
| Package | Version Required | Notes |
|---------|-----------------|-------|
| opencv-python | 4.13+ | Core CV — up to date |
| numpy | 2.4+ | Up to date |
| Pillow | 12.1+ | Up to date |
| scipy | 1.17+ | Up to date |
| requests | 2.32+ | Up to date |

### 3.2 GUI (`requirements_gui.txt`)
| Package | Version Required | Notes |
|---------|-----------------|-------|
| PySide6 | 6.11+ | Up to date |

### 3.3 Development
| Package | Version Required | Notes |
|---------|-----------------|-------|
| black | 26.3+ | Code formatter |
| pytest | 9.0+ | Test runner |

### 3.4 External Dependencies
- **Blender 4.2+** — Required for 3D scene generation. Not installable via pip. Must be present on the system and path configured in `Configs/system.ini`.

### 3.5 Dependency Issues
- No `requirements_server.txt` — Flask and server dependencies are undocumented.
- No pinned versions (no `==`), only minimum bounds (`>=`). This can cause reproducibility issues.
- No `requirements_dev.txt` separating dev tools from runtime.

---

## 4. Configuration Audit

### 4.1 `Configs/default.ini`
Controls per-floorplan settings: image path, transform, feature detection, calibration.

**Issues:**
- `STR_OVERWRITE_DATA` option exists in `config.py` but is marked as **not implemented** (line 46).
- No validation of config values at load time.

### 4.2 `Configs/system.ini`
Controls system-level settings: Blender executable path, output format, overwrite behavior.

**Issues:**
- Blender path auto-detection may be slow on macOS with large volumes (noted in `IO.py` line 77).
- No fallback if Blender is not found — pipeline will fail silently or with a cryptic error.

---

## 5. Core Library Audit (`FloorplanToBlenderLib/`)

### 5.1 Module Responsibilities

| Module | Role |
|--------|------|
| `image.py` | Image preprocessing — rescale, denoise |
| `detect.py` | CV detection — walls, rooms, doors, windows |
| `generate.py` | Orchestrates 3D data generation |
| `generator.py` | Creates Floor, Wall, Room, Door, Window geometry |
| `transform.py` | Converts 2D contours to 3D vertex/face arrays |
| `IO.py` | File I/O, image reading, data persistence |
| `config.py` | INI config loading |
| `const.py` | Constants and magic numbers |
| `execution.py` | Orchestrates single/stacked/cylindrical layouts |
| `calculate.py` | Math utilities |
| `draw.py` | Debug drawing utilities |
| `dialog.py` | CLI dialog helpers |
| `stacking.py` | Multi-floor stacking logic |
| `floorplan.py` | Floorplan data model |
| `exceptions.py` | Custom exceptions |
| `__init__.py` | Package init |

### 5.2 Known Bugs & Limitations

| File | Line | Issue |
|------|------|-------|
| `const.py` | 40 | Only a single door model is supported |
| `const.py` | 102 | Debug visualization not wired for all feature types |
| `detect.py` | 459 | Redundant grayscale conversion |
| `detect.py` | 480 | Door may match multiple boxes; only first is used (silent data loss) |
| `generator.py` | 335 | Windows don't fill small gaps between windows and walls |
| `transform.py` | 120 | `flatten_iterative_safe()` marked as "stopped working" — dead code |
| `image.py` | 71 | Missing print/log when image is rescaled |
| `config.py` | 46 | `STR_OVERWRITE_DATA` not implemented |

### 5.3 Code Quality Issues

- **Type hints**: Inconsistent across modules. Some functions fully typed, others have none.
- **Docstrings**: Many functions lack docstrings, especially in `detect.py` and `generator.py`.
- **Magic numbers**: `const.py` contains many hardcoded calibration values with no explanation of their origin or meaning.
- **Error handling**: Limited try/except blocks. Most errors propagate up or are swallowed by logging.
- **Pyre suppression**: Multiple files use `# pyre-ignore-all-errors`, indicating unresolved type issues that were suppressed rather than fixed.
- **Dead code**: `flatten_iterative_safe()` in `transform.py` is broken and unused but not removed.

---

## 6. Blender Scripts Audit (`Blender/`)

| Script | Role |
|--------|------|
| `build_3d_scene.py` | Reads JSON geometry, builds Blender scene hierarchy |
| `export_format_converter.py` | Converts to OBJ, FBX, GLTF, X3D, BLEND |
| `export_obj_only.py` | OBJ-specific export |
| `open_blend_file.py` | Opens existing .blend file |
| `reformat_object.py` | Reformats object geometry |

### 6.1 Issues

- **Path handling inconsistency** (`build_3d_scene.py` lines 155–180): Mixed use of forward slashes and backslashes. Will cause failures on Windows without normalization.
- **Tight coupling**: Scripts receive data via CLI args and JSON files. No abstraction layer — changing the data format requires updating both the library and all Blender scripts.
- **No error handling inside Blender scripts**: If JSON data is malformed, Blender will crash with a Python traceback rather than a user-friendly error.

---

## 7. GUI Audit (`gui/`, `gui_converter.py`)

### 7.1 Components

| File | Role |
|------|------|
| `gui_converter.py` | Main window — 3-page stacked UI (Convert, History, Settings) |
| `gui/theme.py` | Centralized dark palette |
| `gui/widgets.py` | Reusable button factories |
| `gui/upload_zone.py` | Drag-and-drop image upload widget |
| `gui/worker.py` | Background conversion thread with progress signals |

### 7.2 Issues

- **No input validation** before starting conversion — invalid image paths or missing Blender path can cause worker thread crashes.
- **Worker thread error handling**: Unclear if all exceptions in the worker are caught and surfaced to the UI.
- **History page**: Unclear if history is persisted between sessions or only in-memory.
- **Settings page**: Blender path setting — no verification that the entered path is a valid Blender executable.
- **836-line main file**: `gui_converter.py` is large and could benefit from splitting into sub-modules.

---

## 8. Server/API Audit (`Server/`)

### 8.1 Structure

| Path | Role |
|------|------|
| `Server/main.py` | Flask app entry point |
| `Server/api/` | Route handlers (get, post, put) |
| `Server/process/` | Processing logic |
| `Server/file/` | File handling |
| `Server/flask/` | Templates and static assets |
| `Server/swagger/` | Swagger UI and JSON generation |
| `Server/config/` | Server config handler |
| `Server/shared_variables.py` | Shared state between requests |

### 8.2 Critical Issues

| File | Line | Issue | Severity |
|------|------|-------|----------|
| `shared_variables.py` | 16 | Thread safety not implemented | HIGH |
| `process/evaluate.py` | — | Unimplemented | MEDIUM |
| `process/reformat.py` | — | Unimplemented | MEDIUM |
| `process/resize.py` | — | Unimplemented | MEDIUM |
| `process/filter.py` | — | Unimplemented | MEDIUM |
| `process/compare.py` | — | Unimplemented | MEDIUM |
| `swagger/json_generator.py` | multiple | Swagger generation incomplete (TODOs) | LOW |

### 8.3 Security Concerns

- **No authentication/authorization** visible in the API routes. Any client can submit processing jobs.
- **File upload handling**: No visible file type validation or size limits on uploaded images — potential for abuse.
- **Shared mutable state** (`shared_variables.py`) without thread locks is a race condition waiting to happen under concurrent requests.
- **No rate limiting** documented.

---

## 9. Testing Audit

### 9.1 Current State

- Only one test file found: `Testing/test_calculate.py` (stub).
- No tests for detection, generation, transformation, GUI, or API.
- `pytest` is listed as a dev dependency but barely used.

### 9.2 Coverage Gaps

| Area | Test Coverage |
|------|--------------|
| `FloorplanToBlenderLib/calculate.py` | Stub only |
| `FloorplanToBlenderLib/detect.py` | None |
| `FloorplanToBlenderLib/generate.py` | None |
| `FloorplanToBlenderLib/transform.py` | None |
| `FloorplanToBlenderLib/IO.py` | None |
| GUI components | None |
| Server API endpoints | None |
| Blender scripts | None (not easily testable) |

---

## 10. Documentation Audit

| Item | Status |
|------|--------|
| `README.md` | Present — covers setup and basic usage |
| `Server/README.md` | Present — covers server setup |
| Inline docstrings | Sparse — many functions undocumented |
| API documentation | Swagger present but incomplete |
| Architecture docs | None |
| Contribution guide | None |
| Changelog | None |

---

## 11. End-to-End Flow Summary

```
[Image Input]
     │
     ▼
[image.py] → Rescale, denoise, preprocess
     │
     ▼
[detect.py] → Detect walls, rooms, doors, windows (OpenCV)
     │
     ▼
[generate.py / generator.py] → Build 3D vertex/face data
     │
     ▼
[transform.py] → Convert 2D contours → 3D arrays
     │
     ▼
[IO.py] → Write JSON geometry files to Data/
     │
     ▼
[Blender subprocess] → build_3d_scene.py reads JSON → builds .blend
     │
     ▼
[export_format_converter.py] → Convert to OBJ/FBX/GLTF/etc.
     │
     ▼
[Output file in Target/]
```

---

## 12. Prioritized Recommendations

### Critical (Fix First)
1. **Thread safety in Server** — Add locks around `shared_variables.py` before any production use.
2. **API security** — Add authentication (even basic API key) and file upload validation.
3. **Windows path handling** — Normalize all paths in `build_3d_scene.py` using `os.path.normpath()`.
4. **Remove dead code** — Delete or fix `flatten_iterative_safe()` in `transform.py`.

### High Priority
5. **Error handling in Blender scripts** — Wrap JSON parsing in try/except with meaningful exit codes.
6. **Blender path validation** — Verify executable exists and is callable before starting conversion.
7. **Worker thread error surfacing** — Ensure all exceptions in `gui/worker.py` emit error signals to the UI.
8. **Implement `STR_OVERWRITE_DATA`** in `config.py` or remove the option entirely.

### Medium Priority
9. **Pin dependency versions** — Use `==` in requirements files for reproducible builds.
10. **Add `requirements_server.txt`** — Document Flask and server-side dependencies.
11. **Expand test coverage** — At minimum, unit test `calculate.py`, `transform.py`, and `detect.py`.
12. **Add docstrings** — Prioritize `detect.py`, `generator.py`, and `generate.py`.
13. **Implement or remove stub server modules** — `evaluate.py`, `reformat.py`, `resize.py`, `filter.py`, `compare.py`.

### Low Priority
14. **Complete Swagger documentation**.
15. **Split `gui_converter.py`** into smaller sub-modules.
16. **Add a CHANGELOG.md**.
17. **Add a CONTRIBUTING.md**.
18. **Explain magic numbers** in `const.py` with comments.
19. **Resolve Pyre type errors** instead of suppressing them.

---

## 13. Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| Architecture | 7/10 | Clean separation of concerns; tight Blender coupling is a trade-off |
| Code Quality | 5/10 | Inconsistent typing, sparse docs, dead code, magic numbers |
| Testing | 1/10 | Near zero coverage |
| Security | 3/10 | No auth, no thread safety, no upload validation |
| Documentation | 5/10 | README exists but inline docs are sparse |
| Dependencies | 6/10 | Up-to-date but unpinned and incomplete for server |
| Error Handling | 4/10 | Limited; Blender scripts especially fragile |

**Overall: 4.4 / 10** — Functional prototype quality. Needs hardening before production use.

---

*Audit generated by Kiro — April 16, 2026*
