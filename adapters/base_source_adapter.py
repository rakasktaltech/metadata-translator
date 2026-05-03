from abc import ABC, abstractmethod


class BaseSourceAdapter(ABC):

    @property
    @abstractmethod
    def required_source_files(self) -> dict:
        """Maps each source file role key to a human-readable label."""

    @abstractmethod
    def required_columns(self, file_key: str) -> list:
        """Returns the column names the CSV for the given file role must contain."""

    @property
    @abstractmethod
    def available_config_options(self) -> dict:
        """Maps each integer-choice parameter name to a {int: description_str} dict."""

    @abstractmethod
    def get_config(self) -> dict:
        """Returns the current configuration state."""

    @abstractmethod
    def set_config(self, req):
        """Applies one config parameter change. Returns ConfigSetResponse."""

    @abstractmethod
    def validate_schema(self, req):
        """Validates source DataFrames against required columns. Returns SchemaValidationResponse."""

    @abstractmethod
    def process_sources(self, source_dfs: dict):
        """Processes source DataFrames into ProcessedGlossaryData."""
