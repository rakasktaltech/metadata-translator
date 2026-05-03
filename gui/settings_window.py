import tkinter as tk
from tkinter import ttk


class SettingsWindow(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._error_var = tk.StringVar()
        self._translate_btn = None

        # Track previous valid values so we can revert on ConfigSetResponse failure
        self._prev_source = {}
        self._prev_target = {}

        # StringVar / IntVar references keyed by parameter name
        self._source_vars = {}
        self._target_vars = {}

        self._build()

    # ------------------------------------------------------------------ #
    # Layout construction
    # ------------------------------------------------------------------ #

    def _build(self):
        self.columnconfigure(0, weight=1)

        # Title
        ttk.Label(
            self, text="Settings",
            font=("TkDefaultFont", 13, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 6))

        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, sticky="ew", padx=10)

        # Source settings
        src_config = self._controller.get_source_adapter_config()
        src_options = self._controller.get_source_adapter_options()
        src_name = type(self._controller.source_adapter).__name__.replace("Adapter", "").replace("Statistics", "Statistics ").strip()
        # Use display_name if available
        src_display = getattr(self._controller.source_adapter, 'display_name', src_name)

        src_frame = ttk.LabelFrame(self, text=f"Source: {src_display}")
        src_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=8)
        src_frame.columnconfigure(1, weight=1)
        self._build_source_fields(src_frame, src_config, src_options)

        # Target settings
        tgt_display = getattr(self._controller.target_adapter, 'display_name', 'Target')
        tgt_config = self._controller.get_target_adapter_config()

        tgt_frame = ttk.LabelFrame(self, text=f"Target: {tgt_display}")
        tgt_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=8)
        tgt_frame.columnconfigure(1, weight=1)
        self._build_target_fields(tgt_frame, tgt_config)

        ttk.Separator(self, orient="horizontal").grid(
            row=4, column=0, sticky="ew", padx=10)

        # Error label
        ttk.Label(
            self, textvariable=self._error_var, foreground="red", wraplength=560,
        ).grid(row=5, column=0, sticky="w", padx=20, pady=(4, 0))

        # Bottom bar
        bottom = ttk.Frame(self)
        bottom.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        bottom.columnconfigure(1, weight=1)
        ttk.Button(bottom, text="\u2190 Back", command=self._on_back).grid(
            row=0, column=0, sticky="w")
        self._translate_btn = ttk.Button(bottom, text="Translate", command=self._on_translate)
        self._translate_btn.grid(row=0, column=2, sticky="e")

    def _build_source_fields(self, frame, config: dict, options: dict):
        """Build entry and option-menu widgets for the source adapter config."""
        prefix_suffix_params = [
            'data_term_prefix', 'data_term_suffix',
            'business_term_prefix', 'business_term_suffix',
        ]
        option_params = ['data_term_duplicate', 'data_term_description', 'technical_fields']

        labels = {
            'data_term_prefix':      'Data term prefix:',
            'data_term_suffix':      'Data term suffix:',
            'business_term_prefix':  'Business term prefix:',
            'business_term_suffix':  'Business term suffix:',
            'data_term_duplicate':   'Duplicate handling:',
            'data_term_description': 'Description source:',
            'technical_fields':      'Technical fields:',
        }

        row_idx = 0
        for param in prefix_suffix_params:
            if param not in config:
                continue
            var = tk.StringVar(value=config[param])
            self._source_vars[param] = var
            self._prev_source[param] = config[param]
            ttk.Label(frame, text=labels.get(param, param)).grid(
                row=row_idx, column=0, sticky="w", padx=(8, 10), pady=4)
            entry = ttk.Entry(frame, textvariable=var, width=16)
            entry.grid(row=row_idx, column=1, sticky="w", pady=4)
            entry.bind("<FocusOut>", lambda e, p=param, v=var: self._on_source_entry_changed(p, v))
            row_idx += 1

        for param in option_params:
            if param not in config or param not in options:
                continue
            opts_dict = options[param]
            var = tk.IntVar(value=config[param])
            self._source_vars[param] = var
            self._prev_source[param] = config[param]
            ttk.Label(frame, text=labels.get(param, param)).grid(
                row=row_idx, column=0, sticky="w", padx=(8, 10), pady=4)
            # Build OptionMenu with integer keys but string display values
            menu_values = [opts_dict[k] for k in sorted(opts_dict)]
            display_var = tk.StringVar(value=opts_dict[config[param]])
            option_menu = ttk.Combobox(
                frame, textvariable=display_var,
                values=menu_values, state="readonly", width=40,
            )
            option_menu.grid(row=row_idx, column=1, sticky="w", pady=4)
            # Bind selection: map display string back to int key
            int_by_label = {v: k for k, v in opts_dict.items()}
            option_menu.bind(
                "<<ComboboxSelected>>",
                lambda e, p=param, dv=display_var, ibl=int_by_label:
                    self._on_source_option_changed(p, ibl[dv.get()]),
            )
            row_idx += 1

    def _build_target_fields(self, frame, config: dict):
        """Build entry widgets for target adapter config (string params)."""
        labels = {
            'connection': 'Connection:',
            'schema':     'Schema:',
            'owner':      'Owner:',
            'color':      'Color:',
        }
        row_idx = 0
        for param, value in config.items():
            var = tk.StringVar(value=value)
            self._target_vars[param] = var
            self._prev_target[param] = value
            ttk.Label(frame, text=labels.get(param, f"{param}:")).grid(
                row=row_idx, column=0, sticky="w", padx=(8, 10), pady=4)
            entry = ttk.Entry(frame, textvariable=var, width=40)
            entry.grid(row=row_idx, column=1, sticky="w", pady=4)
            entry.bind("<FocusOut>", lambda e, p=param, v=var: self._on_target_entry_changed(p, v))
            row_idx += 1

    # ------------------------------------------------------------------ #
    # Event handlers
    # ------------------------------------------------------------------ #

    def _on_source_entry_changed(self, param: str, var: tk.StringVar):
        value = var.get()
        resp = self._controller.on_setting_changed('source', param, value)
        if resp.success:
            self._prev_source[param] = value
            self._error_var.set("")
        else:
            var.set(self._prev_source[param])
            self._error_var.set(resp.error)

    def _on_source_option_changed(self, param: str, int_value: int):
        resp = self._controller.on_setting_changed('source', param, int_value)
        if resp.success:
            self._prev_source[param] = int_value
            self._error_var.set("")
        else:
            self._error_var.set(resp.error)

    def _on_target_entry_changed(self, param: str, var: tk.StringVar):
        value = var.get()
        resp = self._controller.on_setting_changed('target', param, value)
        if resp.success:
            self._prev_target[param] = value
            self._error_var.set("")
        else:
            var.set(self._prev_target[param])
            self._error_var.set(resp.error)

    def _on_back(self):
        self._controller.show_adapter_selection()

    def _on_translate(self):
        self._error_var.set("")
        if self._translate_btn is not None:
            self._translate_btn.state(["disabled"])
        try:
            self._controller.on_translate()
        finally:
            if self._translate_btn is not None:
                try:
                    self._translate_btn.state(["!disabled"])
                except tk.TclError:
                    pass  # window may have been replaced

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def show_error(self, message: str):
        self._error_var.set(message)

    def show(self):
        self.pack(fill=tk.BOTH, expand=True)
