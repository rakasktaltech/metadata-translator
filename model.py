import csv
import os

import pandas as pd

from messages import (
    FileValidationRequest, FileValidationResponse,
    ReadinessResponse, ProcessResponse,
    SchemaValidationRequest,
)


class TranslationModel:

    @staticmethod
    def _apply_target_config(data, target_adapter):
        config = target_adapter.get_config()

        df_term = data.df_term.copy()
        df_col_term_rel = data.df_col_term_rel.copy()
        df_term_rel = data.df_term_rel.copy()

        for column in ('color', 'owner'):
            if column in df_term.columns:
                df_term[column] = config.get(column, '')

        for column in ('connection', 'schema'):
            if column in df_col_term_rel.columns:
                df_col_term_rel[column] = config.get(column, '')

        return data._replace(
            df_term=df_term,
            df_col_term_rel=df_col_term_rel,
            df_term_rel=df_term_rel,
        )

    def validate_input_file(self, req: FileValidationRequest) -> FileValidationResponse:
        path = req.path
        if not os.path.isabs(path):
            return FileValidationResponse(valid=False, error=f"Path must be absolute: {path}")
        if not os.path.isfile(path):
            return FileValidationResponse(valid=False, error=f"File not found: {path}")
        if not path.lower().endswith('.csv'):
            return FileValidationResponse(valid=False, error="File must have a .csv extension")
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                first_row = next(reader, None)
                if first_row is None or len(first_row) < 1:
                    return FileValidationResponse(
                        valid=False,
                        error="File is empty or not a valid semicolon-delimited CSV",
                    )
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            return FileValidationResponse(valid=False, error=f"Cannot read file: {exc}")
        return FileValidationResponse(valid=True, error=None)

    def validate_output_file(self, req: FileValidationRequest) -> FileValidationResponse:
        path = req.path
        if not path.lower().endswith('.csv'):
            return FileValidationResponse(valid=False, error="Output file must have a .csv extension")
        directory = os.path.dirname(path)
        if directory and not os.path.isdir(directory):
            return FileValidationResponse(valid=False, error=f"Directory does not exist: {directory}")
        if os.path.exists(path):
            return FileValidationResponse(valid=False, error="File already exists — overwriting is not allowed")
        return FileValidationResponse(valid=True, error=None)

    def check_readiness(self, req) -> ReadinessResponse:
        errors = []
        for key, path in req.source_paths.items():
            if not path:
                errors.append(f"Source file path for '{key}' is empty")
        if not req.connection:
            errors.append("Connection name is required but not set")
        return ReadinessResponse(ready=len(errors) == 0, errors=errors)

    def process(self, req) -> ProcessResponse:
        # Load source CSVs
        source_dfs = {}
        for file_key, path in req.source_paths.items():
            try:
                source_dfs[file_key] = pd.read_csv(path, delimiter=';', encoding='utf-8')
            except Exception as exc:
                return ProcessResponse(success=False, errors=[f"Cannot read '{file_key}': {exc}"], data=None)

        # Validate schema
        schema_req = SchemaValidationRequest(source_dfs=source_dfs)
        schema_resp = req.source_adapter.validate_schema(schema_req)
        if not schema_resp.valid:
            return ProcessResponse(success=False, errors=schema_resp.errors, data=None)

        # Run source adapter processing
        try:
            data = req.source_adapter.process_sources(source_dfs)
        except Exception as exc:
            return ProcessResponse(success=False, errors=[f"Processing error: {exc}"], data=None)

        data = self._apply_target_config(data, req.target_adapter)

        return ProcessResponse(success=True, errors=[], data=data)
