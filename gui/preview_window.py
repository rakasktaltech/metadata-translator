import tkinter as tk
from tkinter import ttk


class PreviewWindow(tk.Frame):

    def __init__(self, parent, controller, data):
        super().__init__(parent)
        self._controller = controller
        self._data = data
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(
            self,
            text="Translation Preview",
            font=("TkDefaultFont", 13, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 6))

        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))

        tab_specs = [
            ('terms', 'Terms', self._data.df_term),
            ('col_term_rel', 'Column\u2013Term Relations', self._data.df_col_term_rel),
            ('term_rel', 'Term Relations', self._data.df_term_rel),
        ]

        for file_key, title, dataframe in tab_specs:
            columns = self._get_columns(file_key, dataframe)
            tab = ttk.Frame(notebook)
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(1, weight=1)

            ttk.Label(tab, text=f"{len(dataframe.index)} rows").grid(
                row=0, column=0, sticky="w", padx=8, pady=(8, 4))

            tree_frame = ttk.Frame(tab)
            tree_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
            tree_frame.columnconfigure(0, weight=1)
            tree_frame.rowconfigure(0, weight=1)

            tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
            tree.grid(row=0, column=0, sticky="nsew")

            y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            y_scroll.grid(row=0, column=1, sticky="ns")
            x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
            x_scroll.grid(row=1, column=0, sticky="ew")
            tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

            self._configure_tree(tree, columns, dataframe)

            notebook.add(tab, text=title)

        bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        bottom.columnconfigure(1, weight=1)

        ttk.Button(bottom, text="\u2190 Reject", command=self._controller.on_preview_rejected).grid(
            row=0, column=0, sticky="w")
        ttk.Button(bottom, text="Accept \u2192", command=self._controller.on_preview_accepted).grid(
            row=0, column=2, sticky="e")

    def _get_columns(self, file_key: str, dataframe):
        try:
            columns = self._controller.target_adapter.output_columns(file_key)
        except NotImplementedError:
            columns = []
        return columns or list(dataframe.columns)

    @staticmethod
    def _configure_tree(tree: ttk.Treeview, columns: list, dataframe):
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=140, minwidth=100, stretch=True)

        for _, row in dataframe.iterrows():
            values = ["" if value is None else str(value) for value in row.reindex(columns).tolist()]
            tree.insert("", tk.END, values=values)

    def show(self):
        self.pack(fill=tk.BOTH, expand=True)