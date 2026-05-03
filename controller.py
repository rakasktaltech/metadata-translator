import tkinter as tk
from tkinter import messagebox

from adapters import BaseSourceAdapter, BaseTargetAdapter  # also registers subclasses
from messages import FileValidationRequest, ReadinessRequest, ProcessRequest, ConfigSetRequest
from model import TranslationModel
from gui.adapter_selection_window import AdapterSelectionWindow
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

        self.pending_data = process_resp.data
        # Stage 2 stub — Stage 3 replaces this with self.show_preview(self.pending_data)
        messagebox.showinfo("Stage 3", "Stage 3 not yet implemented.")
