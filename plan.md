# Metadata Migration Tool — Implementation Plan

## Overview

Migrate the existing CLI `translator.py` into the full MVC + adapter + tkinter architecture defined in SPEC.md.
Delivered across 4 runnable stages — one window (plus all required backend) per stage.
Each stage replaces the missing next window with a stub dialog so the app is always launchable and testable.

---

## Stage 1 — Foundation + Window 1 (Adapter Selection)

**Goal:** `python main.py` opens Window 1. Browse source files, click Next → validates both paths → stub dialog "Stage 2 not yet implemented."

### New files

| File | Contents |
|---|---|
| `messages.py` | All 9 named tuples: `FileValidationRequest/Response`, `ConfigSetRequest/Response`, `ReadinessRequest/Response`, `SchemaValidationRequest/Response`, `ProcessedGlossaryData`, `ProcessRequest/Response`, `WriteOutputRequest/Response` |
| `adapters/__init__.py` | Empty package marker |
| `adapters/base_source_adapter.py` | ABC with abstract methods: `required_source_files`, `required_columns`, `available_config_options`, `get_config`, `set_config`, `validate_schema`, `process_sources` |
| `adapters/base_target_adapter.py` | ABC with abstract methods: `required_target_files`, `output_columns`, `get_config`, `set_config`, `write_output` |
| `adapters/statistics_estonia_adapter.py` | Stub — implements `required_source_files`, `required_columns`, `available_config_options`, `get_config`, `set_config`, `validate_schema` only; `process_sources` raises `NotImplementedError` |
| `adapters/select_zero_adapter.py` | Stub — implements `required_target_files`, `output_columns`, `get_config`, `set_config` only; `write_output` and source methods raise `NotImplementedError` |
| `model.py` | `validate_input_file`, `validate_output_file` only (migrated from `translator.py` `is_correct_input` / `is_correct_output`) |
| `controller.py` | Owns `Tk` root; `show_adapter_selection`; `on_adapters_selected` (runs file validation loop → stub messagebox on success) |
| `gui/__init__.py` | Empty package marker |
| `gui/adapter_selection_window.py` | Full Window 1: source/target adapter dropdowns, dynamic file-path rows (rebuilt when adapter changes), inline error label, Next button (disabled until all entries filled) |

### Modified files

| File | Change |
|---|---|
| `main.py` | Replace console loop with `root = tk.Tk()` + `Controller(root).start()` + `root.mainloop()` |

### Verification
- `python main.py` → Window 1 renders
- Browse both CSV files → paths appear in entries
- Next button enables; click → validates paths → stub "Stage 2 not yet implemented" dialog appears
- Invalid path → red inline error label shown without leaving Window 1

---

## Stage 2 — Settings Window + Full Translation Pipeline

**Goal:** Window 1 → Window 2. All settings configurable. Translate runs full pipeline. Success → stub dialog; failure → inline error.

### New files

| File | Contents |
|---|---|
| `gui/settings_window.py` | Full Window 2: source `LabelFrame` with 4 prefix/suffix `Entry` widgets + 3 `OptionMenu` widgets; target `LabelFrame` with 4 `Entry` widgets; inline error label; Back and Translate buttons |

### Modified files

| File | Change |
|---|---|
| `adapters/statistics_estonia_adapter.py` | Add `process_sources`: migrate `resolve_data_glossary` + `resolve_business_glossary` from `translator.py` with all Known Issues fixed — `seen_terms` set initialised before loop; inverted guard corrected; DataFrames created fresh per call (no class-level shared state) |
| `model.py` | Add `check_readiness` (validates `source_paths` non-empty + `connection` non-empty); add `process` (load CSVs → `SchemaValidationRequest` → `process_sources` → `ProcessResponse`) |
| `controller.py` | Add `show_settings`; `on_setting_changed` (dispatches `ConfigSetRequest`, reverts entry on failure); `on_translate` (calls `check_readiness` then `process`; on success: stub `messagebox.showinfo("Preview coming in Stage 3")`) |

### Bug fixes from Known Issues applied in this stage

| Issue | Fix |
|---|---|
| `term_list` re-initialised inside loop → deduplication never triggers | `seen_terms = set()` initialised once before the `for` loop |
| Guard `if pd.notna(...): continue` has inverted logic | Invert to `if pd.isna(...) or ...: continue` (skip when fields absent) |
| Class-level shared mutable DataFrames | All DataFrames created inside `process_sources`; no instance or class variables carry state between calls |

### Verification
- Navigate Window 1 → Window 2
- Change duplicate option dropdown → `ConfigSetRequest` sent, value updates
- Enter invalid connection (1 char) → entry reverts, inline error shown
- Enter valid connection, click Translate with sample CSVs → stub success dialog
- Translate with bad CSV path → inline error shown, no crash

---

## Stage 3 — Preview Window

**Goal:** Full Windows 1 → 2 → 3. Reject returns to Settings (state preserved, settings not reset). Accept → stub "Stage 4 coming."

### New files

| File | Contents |
|---|---|
| `gui/preview_window.py` | Full Window 3: `ttk.Notebook` with 3 tabs ("Terms", "Column–Term Relations", "Term Relations"); each tab has a `ttk.Treeview` (`show="headings"`) with vertical + horizontal `ttk.Scrollbar`; row-count label per tab; Reject and Accept buttons |

### Modified files

| File | Change |
|---|---|
| `adapters/select_zero_adapter.py` | Complete `output_columns` to return correct column list per file-key: `terms` → `['name','color','description','type','domain','owner']`; `col_term_rel` → `['connection','schema','object','column','term']`; `term_rel` → `['sourceName','relation','targetName']` |
| `controller.py` | Add `show_preview(data)` (destroys current frame, packs `PreviewWindow`); `on_preview_accepted` (stores `data` in `self.pending_data`, stub messagebox); `on_preview_rejected` (clears `pending_data`, calls `show_settings`) |

### Verification
- Full flow Windows 1 → 2 → 3
- All three tabs render with correct columns and populated rows
- Scrollbars functional
- Reject → back to Window 2 with previously entered settings still populated
- Accept → stub dialog appears

---

## Stage 4 — Output Selection + Write + Tests

**Goal:** Complete end-to-end application. Write output files, success dialog, app exits. Full test suite passes.

### New files

| File | Contents |
|---|---|
| `gui/output_selection_window.py` | Full Window 4: dynamic output-path rows (one per `required_target_files` key), Browse uses `asksaveasfilename`, inline error label, Back and Write buttons; success → `messagebox.showinfo` listing written paths → `root.destroy()` |
| `tests/test_model.py` | pytest unit tests covering: `validate_input_file` (valid + invalid cases), `validate_output_file` (valid + overwrite + bad ext), `check_readiness`, `process` with sample CSVs, `StatisticsEstoniaAdapter.set_config` (valid/invalid values), `validate_schema` (missing columns) |

### Modified files

| File | Change |
|---|---|
| `adapters/select_zero_adapter.py` | Add `write_output(data, target_paths)`: writes `df_term`, `df_col_term_rel`, `df_term_rel` as UTF-8 semicolon-delimited CSV files to the three target paths |
| `adapters/statistics_estonia_adapter.py` | Add `write_output(data, target_paths)` (as target adapter): serialises `ProcessedGlossaryData` back to Statistics Estonia-compatible CSVs |
| `model.py` | Add `write_output(req: WriteOutputRequest) → WriteOutputResponse`: delegates to `target_adapter.write_output(data, target_paths)`; returns paths list on success, error list on failure |
| `controller.py` | Add `show_output_selection`; `on_write(target_paths)`: validation loop (non-empty, no duplicates with source paths, `FileValidationRequest` per path) → `WriteOutputRequest` → `WriteOutputResponse`; success dialog + `self.root.destroy()` |

### Verification
- `python main.py` — full end-to-end run writes 3 CSV files
- Success dialog lists all 3 file paths; dismissing it closes the app
- Attempt to write to existing file → inline error, no overwrite
- `pytest tests/test_model.py` — all tests pass

---

## File Structure After Stage 4

```
hobby_projects/
├── main.py                                  # Tk root + Controller wiring
├── controller.py                            # All navigation + request dispatch
├── model.py                                 # Validation + pipeline orchestration
├── messages.py                              # Named tuple definitions
├── plan.md                                  # This file
├── adapters/
│   ├── __init__.py
│   ├── base_source_adapter.py
│   ├── base_target_adapter.py
│   ├── statistics_estonia_adapter.py
│   └── select_zero_adapter.py
├── gui/
│   ├── __init__.py
│   ├── adapter_selection_window.py
│   ├── settings_window.py
│   ├── preview_window.py
│   └── output_selection_window.py
├── tests/
│   ├── conftest.py
│   ├── test_model.py                        # New pytest suite
│   └── test_translator.py                   # Existing tests (kept, not deleted)
├── test_business_glossary.csv
├── test_data_glossary.csv
└── test archive/
    └── ...
```

---

## Notes

- `translator.py` and the old `main.py` console loop are superseded by the new architecture but `translator.py` is kept as reference until Stage 4 is complete
- `SelectZeroAdapter.process_sources` (reading SelectZero CSVs as a source format) is scaffolded in Stage 1 but left raising `NotImplementedError` — no sample SelectZero input files exist to test against
- `tests/test_translator.py` remains and continues to pass throughout all stages; it is not deleted
