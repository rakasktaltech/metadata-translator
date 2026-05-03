"""
Controller tests run headless using Tk() in withdraw mode so no window appears.
Only non-GUI logic is tested (adapter registry, query helpers, on_adapters_selected).
"""
import os
import tkinter as tk
import pytest
from unittest.mock import MagicMock, patch

from controller import Controller
from adapters import StatisticsEstoniaAdapter, SelectZeroAdapter
from messages import ConfigSetRequest
from gui.preview_window import PreviewWindow


WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALID_BG = os.path.join(WORKSPACE, 'test_business_glossary.csv')
VALID_DG = os.path.join(WORKSPACE, 'test_data_glossary.csv')


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def controller(tk_root):
    ctrl = Controller(tk_root)
    yield ctrl
    if ctrl.current_frame is not None:
        ctrl.current_frame.destroy()
        ctrl.current_frame = None


# --- Adapter registry ---

def test_source_adapter_names_contains_statistics_estonia(controller):
    names = controller.get_source_adapter_names()
    assert 'Statistics Estonia' in names


def test_source_adapter_names_contains_select_zero(controller):
    names = controller.get_source_adapter_names()
    assert 'SelectZero' in names


def test_target_adapter_names_contains_both(controller):
    names = controller.get_target_adapter_names()
    assert 'Statistics Estonia' in names
    assert 'SelectZero' in names


def test_source_and_target_names_match(controller):
    # Both ABCs have the same concrete subclasses
    assert set(controller.get_source_adapter_names()) == set(controller.get_target_adapter_names())


# --- get_source_required_files ---

def test_get_source_required_files_statistics_estonia(controller):
    files = controller.get_source_required_files('Statistics Estonia')
    assert 'business_glossary' in files
    assert 'data_glossary' in files


def test_get_source_required_files_unknown_returns_empty(controller):
    files = controller.get_source_required_files('Nonexistent Adapter')
    assert files == {}


# --- Initial state ---

def test_initial_state_source_adapter_is_none(controller):
    assert controller.source_adapter is None


def test_initial_state_target_adapter_is_none(controller):
    assert controller.target_adapter is None


def test_initial_state_pending_data_is_none(controller):
    assert controller.pending_data is None


def test_initial_state_source_paths_empty(controller):
    assert controller.source_paths == {}


# --- on_adapters_selected with invalid path ---

def test_on_adapters_selected_invalid_path_shows_error(controller):
    controller.current_frame = MagicMock()
    controller.on_adapters_selected(
        'Statistics Estonia',
        'SelectZero',
        {'business_glossary': 'relative_path.csv', 'data_glossary': VALID_DG},
    )
    controller.current_frame.show_error.assert_called_once()
    # Adapters should NOT be instantiated on failure
    assert controller.source_adapter is None


def test_on_adapters_selected_valid_paths_sets_adapters(controller):
    controller.current_frame = MagicMock()
    with patch('controller.messagebox'):
        controller.on_adapters_selected(
            'Statistics Estonia',
            'SelectZero',
            {'business_glossary': VALID_BG, 'data_glossary': VALID_DG},
        )
    assert isinstance(controller.source_adapter, StatisticsEstoniaAdapter)
    assert isinstance(controller.target_adapter, SelectZeroAdapter)


def test_on_adapters_selected_valid_paths_stores_paths(controller):
    controller.current_frame = MagicMock()
    paths = {'business_glossary': VALID_BG, 'data_glossary': VALID_DG}
    with patch('controller.messagebox'):
        controller.on_adapters_selected('Statistics Estonia', 'SelectZero', paths)
    assert controller.source_paths == paths


def test_on_adapters_selected_second_invalid_path_shows_error(controller):
    controller.current_frame = MagicMock()
    controller.on_adapters_selected(
        'Statistics Estonia',
        'SelectZero',
        {'business_glossary': VALID_BG, 'data_glossary': 'bad_path.csv'},
    )
    controller.current_frame.show_error.assert_called_once()
    assert controller.source_adapter is None


def test_on_translate_success_shows_preview_without_storing_pending_data(controller):
    settings_frame = MagicMock()
    controller.current_frame = settings_frame
    controller.source_adapter = StatisticsEstoniaAdapter()
    controller.target_adapter = SelectZeroAdapter()
    controller.target_adapter.set_config(ConfigSetRequest('connection', 'demo_connection'))
    controller.source_paths = {'business_glossary': VALID_BG, 'data_glossary': VALID_DG}

    controller.on_translate()

    settings_frame.show_error.assert_not_called()
    assert isinstance(controller.current_frame, PreviewWindow)
    assert controller.pending_data is None


def test_on_preview_accepted_stores_data_and_shows_stage_4_stub(controller):
    controller.source_adapter = StatisticsEstoniaAdapter()
    controller.target_adapter = SelectZeroAdapter()
    controller.target_adapter.set_config(ConfigSetRequest('connection', 'demo_connection'))
    controller.source_paths = {'business_glossary': VALID_BG, 'data_glossary': VALID_DG}
    controller.on_translate()

    with patch('controller.messagebox.showinfo') as showinfo:
        controller.on_preview_accepted()

    assert controller.pending_data is not None
    showinfo.assert_called_once_with('Stage 4', 'Stage 4 coming soon.')


def test_on_preview_rejected_returns_to_settings_and_clears_pending_data(controller):
    controller.source_adapter = StatisticsEstoniaAdapter()
    controller.target_adapter = SelectZeroAdapter()
    controller.target_adapter.set_config(ConfigSetRequest('connection', 'demo_connection'))
    controller.source_paths = {'business_glossary': VALID_BG, 'data_glossary': VALID_DG}
    controller.pending_data = object()
    controller.on_translate()

    controller.on_preview_rejected()

    assert controller.pending_data is None
    assert controller.root.title() == 'Data Catalog Translator — Settings'
