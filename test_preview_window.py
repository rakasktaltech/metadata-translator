import tkinter as tk

import pandas as pd
import pytest

from adapters import SelectZeroAdapter
from gui.preview_window import PreviewWindow
from messages import ProcessedGlossaryData


class StubController:

    def __init__(self):
        self.target_adapter = SelectZeroAdapter()
        self.accepted = False
        self.rejected = False

    def on_preview_accepted(self):
        self.accepted = True

    def on_preview_rejected(self):
        self.rejected = True


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def preview_data():
    return ProcessedGlossaryData(
        df_term=pd.DataFrame([
            {
                'name': 'term_a',
                'color': 'blue',
                'description': 'desc',
                'type': 'Term',
                'domain': '',
                'owner': 'owner_a',
            }
        ]),
        df_col_term_rel=pd.DataFrame([
            {
                'connection': 'conn',
                'schema': 'public',
                'object': 'table_a',
                'column': 'column_a',
                'term': 'term_a',
            }
        ]),
        df_term_rel=pd.DataFrame([
            {
                'sourceName': 'concept_a',
                'relation': 'Related to',
                'targetName': 'term_a',
            }
        ]),
    )


@pytest.fixture
def stub_controller():
    return StubController()


@pytest.fixture
def window(tk_root, stub_controller, preview_data):
    frame = PreviewWindow(tk_root, stub_controller, preview_data)
    yield frame
    if frame.winfo_exists():
        frame.destroy()


def _find_notebook(window: PreviewWindow) -> tk.Widget:
    return next(child for child in window.winfo_children() if isinstance(child, tk.ttk.Notebook))


def _find_buttons(window: PreviewWindow) -> list:
    return [child for child in window.winfo_children() if isinstance(child, tk.ttk.Frame)][-1].winfo_children()


def test_preview_builds_three_tabs(window):
    notebook = _find_notebook(window)
    assert len(notebook.tabs()) == 3


def test_preview_uses_target_adapter_columns(window):
    notebook = _find_notebook(window)
    first_tab = notebook.nametowidget(notebook.tabs()[0])
    tree_frame = [child for child in first_tab.winfo_children() if isinstance(child, tk.ttk.Frame)][0]
    tree = next(child for child in tree_frame.winfo_children() if isinstance(child, tk.ttk.Treeview))

    assert tree["columns"] == ('name', 'color', 'description', 'type', 'domain', 'owner')
    assert tree.item(tree.get_children()[0], 'values') == ('term_a', 'blue', 'desc', 'Term', '', 'owner_a')


def test_preview_buttons_call_controller(window, stub_controller):
    buttons = _find_buttons(window)
    reject_button = next(button for button in buttons if button.cget('text') == '← Reject')
    accept_button = next(button for button in buttons if button.cget('text') == 'Accept →')

    reject_button.invoke()
    accept_button.invoke()

    assert stub_controller.rejected is True
    assert stub_controller.accepted is True


def test_show_packs_frame(window):
    window.show()
    assert window.winfo_manager() == 'pack'