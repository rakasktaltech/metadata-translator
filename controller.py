import tkinter as tk
from tkinter import messagebox

from adapters import BaseSourceAdapter, BaseTargetAdapter  # also registers subclasses
from messages import (
    FileValidationRequest,
    ReadinessRequest,
    ProcessRequest,
    ConfigSetRequest,
    WriteOutputRequest,
)
from model import TranslationModel
from gui.adapter_selection_window import AdapterSelectionWindow
from gui.output_selection_window import OutputSelectionWindow
from gui.preview_window import PreviewWindow
from gui.settings_window import SettingsWindow


class Controller:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Data Catalog Translator")
        self.root.minsize(640, 380)

        self.model = TranslationModel()

        self._source_adapters = {
            cls.display_name: cls
            for cls in BaseSourceAdapter.__subclasses__()
        }
        self._target_adapters = {
            cls.display_name: cls
            for cls in BaseTargetAdapter.__subclasses__()
        }

        self.source_paths = {}
        self.source_adapter = None
        self.target_adapter = None
        self.pending_data = None
        self.current_frame = None

    def start(self):
        self.show_adapter_selection()

    # ------------------------------------------------------------------ #
    # Window navigation
    # ------------------------------------------------------------------ #

    def show_adapter_selection(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None
        self.root.title("Data Catalog Translator \u2014 Adapter Selection")
        frame = AdapterSelectionWindow(self.root, self)
        frame.show()
        self.current_frame = frame

    # ------------------------------------------------------------------ #
    # Queries used by AdapterSelectionWindow
    # ------------------------------------------------------------------ #

    def get_source_adapter_names(self) -> list:
        return list(self._source_adapters.keys())

    def get_target_adapter_names(self) -> list:
        return list(self._target_adapters.keys())

    def get_source_required_files(self, adapter_name: str) -> dict:
        cls = self._source_adapters.get(adapter_name)
        if cls is None:
            return {}
        return cls().required_source_files

    # ------------------------------------------------------------------ #
    # Callbacks from AdapterSelectionWindow
    # ------------------------------------------------------------------ #

    def on_adapters_selected(self, source_name: str, target_name: str, source_paths: dict):
        for path in source_paths.values():
            req = FileValidationRequest(path=path, file_type='input')
            resp = self.model.validate_input_file(req)
            if not resp.valid:
                self.current_frame.show_error(resp.error)
                return

        self.source_adapter = self._source_adapters[source_name]()
        self.target_adapter = self._target_adapters[target_name]()
        self.source_paths = source_paths

        self.show_settings()

    # ------------------------------------------------------------------ #
    # Window 2 — Settings
    # ------------------------------------------------------------------ #

    def show_settings(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None
        self.root.title("Data Catalog Translator \u2014 Settings")
        frame = SettingsWindow(self.root, self)
        frame.show()
        self.current_frame = frame

    def show_preview(self, data):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None
        self.root.title("Data Catalog Translator \u2014 Translation Preview")
        frame = PreviewWindow(self.root, self, data)
        frame.show()
        self.current_frame = frame

    def show_output_selection(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None
        self.root.title("Data Catalog Translator \u2014 Save Output Files")
        frame = OutputSelectionWindow(self.root, self)
        frame.show()
        self.current_frame = frame

    def get_source_adapter_config(self) -> dict:
        return self.source_adapter.get_config()

    def get_target_adapter_config(self) -> dict:
        return self.target_adapter.get_config()

    def get_source_adapter_options(self) -> dict:
        return self.source_adapter.available_config_options

    def on_setting_changed(self, adapter_side: str, param: str, value):
        if adapter_side == 'source':
            resp = self.source_adapter.set_config(ConfigSetRequest(parameter=param, value=value))
        else:
            resp = self.target_adapter.set_config(ConfigSetRequest(parameter=param, value=value))
        return resp

    def on_translate(self):
        target_config = self.target_adapter.get_config()
        readiness_req = ReadinessRequest(
            source_paths=self.source_paths,
            connection=target_config.get('connection', ''),
        )
        readiness_resp = self.model.check_readiness(readiness_req)
        if not readiness_resp.ready:
            self.current_frame.show_error("\n".join(readiness_resp.errors))
            return

        process_req = ProcessRequest(
            source_paths=self.source_paths,
            source_adapter=self.source_adapter,
            target_adapter=self.target_adapter,
        )
        process_resp = self.model.process(process_req)
        if not process_resp.success:
            self.current_frame.show_error("\n".join(process_resp.errors))
            return

        self.show_preview(process_resp.data)

    def on_preview_accepted(self):
        if isinstance(self.current_frame, PreviewWindow):
            self.pending_data = self.current_frame._data
        if self.pending_data is None:
            return
        self.show_output_selection()

    def on_preview_rejected(self):
        self.pending_data = None
        self.show_settings()

    def on_output_back(self):
        if self.pending_data is not None:
            self.show_preview(self.pending_data)

    def on_write(self, target_paths: dict):
        for file_key, path in target_paths.items():
            if not path:
                self.current_frame.show_error(f"Output file path for '{file_key}' is empty")
                return

        combined_paths = list(self.source_paths.values()) + list(target_paths.values())
        if len(set(combined_paths)) != len(combined_paths):
            self.current_frame.show_error("Source and output paths must all be distinct")
            return

        for path in target_paths.values():
            req = FileValidationRequest(path=path, file_type='output')
            resp = self.model.validate_output_file(req)
            if not resp.valid:
                self.current_frame.show_error(resp.error)
                return

        write_req = WriteOutputRequest(
            data=self.pending_data,
            target_paths=target_paths,
            target_adapter=self.target_adapter,
        )
        write_resp = self.model.write_output(write_req)
        if not write_resp.success:
            self.current_frame.show_error("\n".join(write_resp.errors))
            return

        messagebox.showinfo(
            "Output written",
            "Files written:\n" + "\n".join(write_resp.output_files),
        )
        self.root.destroy()
