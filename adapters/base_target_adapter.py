from abc import ABC, abstractmethod


class BaseTargetAdapter(ABC):

    @property
    @abstractmethod
    def required_target_files(self) -> dict:
        """Maps each output file role key to a human-readable label."""

    @abstractmethod
    def output_columns(self, file_key: str) -> list:
        """Returns the output column names for the given file role key."""

    @abstractmethod
    def get_config(self) -> dict:
        """Returns the current configuration state."""

    @abstractmethod
    def set_config(self, req):
        """Applies one config parameter change. Returns ConfigSetResponse."""

    @abstractmethod
    def write_output(self, data, target_paths: dict):
        """Writes ProcessedGlossaryData to the given target file paths."""
