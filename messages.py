from collections import namedtuple

# --- File validation ---
# Controller -> Model
FileValidationRequest  = namedtuple('FileValidationRequest',  ['path', 'file_type'])
# file_type: 'input' | 'output'
FileValidationResponse = namedtuple('FileValidationResponse', ['valid', 'error'])

# --- Configuration mutation ---
# Controller -> SourceAdapter or TargetAdapter
ConfigSetRequest  = namedtuple('ConfigSetRequest',  ['parameter', 'value'])
ConfigSetResponse = namedtuple('ConfigSetResponse', ['success', 'error'])

# --- Input readiness check (before processing; output paths checked separately) ---
# Controller -> Model
ReadinessRequest  = namedtuple('ReadinessRequest',  ['source_paths', 'connection'])
# source_paths: dict[str, str] — maps file role key to absolute path
ReadinessResponse = namedtuple('ReadinessResponse', ['ready', 'errors'])

# --- Schema validation (Model-internal, forwarded to SourceAdapter) ---
SchemaValidationRequest  = namedtuple('SchemaValidationRequest',  ['source_dfs'])
# source_dfs: dict[str, DataFrame] — same keys as source_paths
SchemaValidationResponse = namedtuple('SchemaValidationResponse', ['valid', 'errors'])

# --- Intermediate data (SourceAdapter -> Model -> PreviewWindow -> OutputSelectionWindow) ---
ProcessedGlossaryData = namedtuple('ProcessedGlossaryData', ['df_term', 'df_col_term_rel', 'df_term_rel'])

# --- Translation processing (load CSVs + run adapters; no file writing) ---
# Controller -> Model  (triggered when SettingsWindow "Translate" is clicked)
ProcessRequest  = namedtuple('ProcessRequest',  ['source_paths', 'source_adapter', 'target_adapter'])
# source_paths: dict[str, str] — maps file role key to absolute path
ProcessResponse = namedtuple('ProcessResponse', ['success', 'errors', 'data'])
# data: ProcessedGlossaryData on success, None on failure

# --- Output file writing (separate step; triggered from OutputSelectionWindow) ---
# Controller -> Model
WriteOutputRequest  = namedtuple('WriteOutputRequest',  ['data', 'target_paths', 'target_adapter'])
# target_paths: dict[str, str] — maps file role key to absolute path
WriteOutputResponse = namedtuple('WriteOutputResponse', ['success', 'errors', 'output_files'])
# output_files: list[str] — absolute paths written; empty list on failure
