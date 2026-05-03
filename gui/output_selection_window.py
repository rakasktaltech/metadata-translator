import tkinter as tk
from tkinter import filedialog, ttk


class OutputSelectionWindow(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._error_var = tk.StringVar()
        self._path_vars = {}
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        ttk.Label(
            self,
            text="Save Output Files",
            font=("TkDefaultFont", 13, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 6))

        files_frame = ttk.Frame(self)
        files_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(6, 8))
        files_frame.columnconfigure(1, weight=1)

        for row_index, (file_key, label_text) in enumerate(
            self._controller.target_adapter.required_target_files.items()
        ):
            path_var = tk.StringVar()
            self._path_vars[file_key] = path_var

            ttk.Label(files_frame, text=f"{label_text}:").grid(
                row=row_index,
                column=0,
                sticky="w",
                padx=(0, 10),
                pady=4,
            )
            ttk.Entry(files_frame, textvariable=path_var, width=60).grid(
                row=row_index,
                column=1,
                sticky="ew",
                pady=4,
            )
            ttk.Button(
                files_frame,
                text="Browse",
                command=lambda key=file_key: self._browse_output(key),
            ).grid(row=row_index, column=2, sticky="e", padx=(8, 0), pady=4)

        ttk.Separator(self, orient="horizontal").grid(
            row=2, column=0, sticky="ew", padx=10)

        ttk.Label(
            self,
            textvariable=self._error_var,
            foreground="red",
            wraplength=560,
        ).grid(row=3, column=0, sticky="w", padx=20, pady=(6, 0))

        bottom = ttk.Frame(self)
        bottom.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        bottom.columnconfigure(1, weight=1)

        ttk.Button(bottom, text="\u2190 Back", command=self._controller.on_output_back).grid(
            row=0, column=0, sticky="w")
        ttk.Button(bottom, text="Write", command=self._on_write).grid(
            row=0, column=2, sticky="e")

    def _browse_output(self, file_key: str):
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
        )
        if path:
            self._path_vars[file_key].set(path)

    def _on_write(self):
        self._error_var.set("")
        self._controller.on_write({
            file_key: path_var.get().strip()
            for file_key, path_var in self._path_vars.items()
        })

    def show_error(self, message: str):
        self._error_var.set(message)

    def show(self):
        self.pack(fill=tk.BOTH, expand=True)