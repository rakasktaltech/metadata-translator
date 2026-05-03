import tkinter as tk
from tkinter import ttk, filedialog


class AdapterSelectionWindow(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._source_var = tk.StringVar()
        self._target_var = tk.StringVar()
        self._path_vars = {}        # file_key -> StringVar
        self._path_frame = None
        self._error_var = tk.StringVar()
        self._next_btn = None
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)   # path area expands

        # Title
        ttk.Label(
            self, text="Data Catalog Translator",
            font=("TkDefaultFont", 13, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 6))

        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, sticky="ew", padx=10)

        # Adapter dropdowns
        adapter_frame = ttk.Frame(self)
        adapter_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=8)

        source_names = self._controller.get_source_adapter_names()
        target_names = self._controller.get_target_adapter_names()

        ttk.Label(adapter_frame, text="Source format:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=4)
        source_cb = ttk.Combobox(
            adapter_frame, textvariable=self._source_var,
            values=source_names, state="readonly", width=32)
        source_cb.grid(row=0, column=1, sticky="w", pady=4)
        default_source = (
            "Statistics Estonia" if "Statistics Estonia" in source_names
            else (source_names[0] if source_names else "")
        )
        self._source_var.set(default_source)
        source_cb.bind("<<ComboboxSelected>>", self._on_source_changed)

        ttk.Label(adapter_frame, text="Target format:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=4)
        target_cb = ttk.Combobox(
            adapter_frame, textvariable=self._target_var,
            values=target_names, state="readonly", width=32)
        target_cb.grid(row=1, column=1, sticky="w", pady=4)
        default_target = (
            "SelectZero" if "SelectZero" in target_names
            else (target_names[0] if target_names else "")
        )
        self._target_var.set(default_target)

        ttk.Separator(self, orient="horizontal").grid(
            row=3, column=0, sticky="ew", padx=10)

        # Dynamic file path section
        self._path_frame = ttk.Frame(self)
        self._path_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=8)
        self._path_frame.columnconfigure(1, weight=1)
        self._rebuild_path_rows()

        ttk.Separator(self, orient="horizontal").grid(
            row=5, column=0, sticky="ew", padx=10)

        # Error label
        ttk.Label(
            self, textvariable=self._error_var, foreground="red",
        ).grid(row=6, column=0, sticky="w", padx=20, pady=(4, 0))

        # Bottom bar with Next button
        bottom = ttk.Frame(self)
        bottom.grid(row=7, column=0, sticky="ew", padx=20, pady=10)
        bottom.columnconfigure(0, weight=1)
        self._next_btn = ttk.Button(bottom, text="Next \u2192", command=self._on_next)
        self._next_btn.grid(row=0, column=1, sticky="e")
        self._update_next_state()

    def _rebuild_path_rows(self):
        for widget in self._path_frame.winfo_children():
            widget.destroy()
        self._path_vars = {}

        adapter_name = self._source_var.get()
        required_files = self._controller.get_source_required_files(adapter_name)

        for i, (file_key, label) in enumerate(required_files.items()):
            var = tk.StringVar()
            var.trace_add("write", lambda *_: self._update_next_state())
            self._path_vars[file_key] = var

            ttk.Label(self._path_frame, text=f"{label}:").grid(
                row=i, column=0, sticky="w", padx=(0, 10), pady=4)
            ttk.Entry(self._path_frame, textvariable=var, width=50).grid(
                row=i, column=1, sticky="ew", pady=4)
            ttk.Button(
                self._path_frame, text="Browse",
                command=lambda k=file_key: self._on_browse(k),
            ).grid(row=i, column=2, padx=(6, 0), pady=4)

        self._update_next_state()

    def _on_source_changed(self, _event=None):
        self._error_var.set("")
        self._rebuild_path_rows()

    def _on_browse(self, file_key):
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            self._path_vars[file_key].set(path)

    def _update_next_state(self):
        if self._next_btn is None:
            return
        all_filled = bool(self._path_vars) and all(
            v.get().strip() for v in self._path_vars.values()
        )
        self._next_btn.state(["!disabled"] if all_filled else ["disabled"])

    def _on_next(self):
        self._error_var.set("")
        source_paths = {k: v.get().strip() for k, v in self._path_vars.items()}
        self._controller.on_adapters_selected(
            self._source_var.get(),
            self._target_var.get(),
            source_paths,
        )

    def show_error(self, message):
        self._error_var.set(message)

    def show(self):
        self.pack(fill=tk.BOTH, expand=True)
