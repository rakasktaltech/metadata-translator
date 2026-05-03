import tkinter as tk
from unittest.mock import MagicMock

import pytest

from adapters import SelectZeroAdapter, StatisticsEstoniaAdapter
from gui.settings_window import SettingsWindow
from messages import ConfigSetResponse


class StubController:

    def __init__(self):
        self.source_adapter = StatisticsEstoniaAdapter()
        self.target_adapter = SelectZeroAdapter()
        self.setting_response = ConfigSetResponse(success=True, error=None)
        self.setting_calls = []
        self.show_adapter_selection = MagicMock()
        self.on_translate = MagicMock()

    def get_source_adapter_config(self):
        return self.source_adapter.get_config()

    def get_target_adapter_config(self):
        return self.target_adapter.get_config()

    def get_source_adapter_options(self):
        return self.source_adapter.available_config_options

    def on_setting_changed(self, adapter_side, param, value):
        self.setting_calls.append((adapter_side, param, value))
        return self.setting_response


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def stub_controller():
    return StubController()


@pytest.fixture
def window(tk_root, stub_controller):
    frame = SettingsWindow(tk_root, stub_controller)
    yield frame
    if frame.winfo_exists():
        frame.destroy()


def test_source_vars_include_all_expected_keys(window):
    assert set(window._source_vars.keys()) == {
        'data_term_prefix',
        'data_term_suffix',
        'business_term_prefix',
        'business_term_suffix',
        'data_term_duplicate',
        'data_term_description',
        'technical_fields',
    }


def test_target_vars_include_all_expected_keys(window):
    assert set(window._target_vars.keys()) == {
        'connection',
        'schema',
        'owner',
        'color',
    }


def test_prev_source_starts_from_source_config(window, stub_controller):
    assert window._prev_source == stub_controller.source_adapter.get_config()


def test_prev_target_starts_from_target_config(window, stub_controller):
    assert window._prev_target == stub_controller.target_adapter.get_config()


def test_source_entry_change_success_updates_previous_value(window, stub_controller):
    var = window._source_vars['data_term_prefix']
    var.set('ab')

    window._on_source_entry_changed('data_term_prefix', var)

    assert stub_controller.setting_calls[-1] == ('source', 'data_term_prefix', 'ab')
    assert window._prev_source['data_term_prefix'] == 'ab'
    assert window._error_var.get() == ''


def test_source_entry_change_failure_reverts_value(window, stub_controller):
    stub_controller.setting_response = ConfigSetResponse(success=False, error='bad prefix')
    window._prev_source['data_term_prefix'] = 'prev'
    var = window._source_vars['data_term_prefix']
    var.set('x')

    window._on_source_entry_changed('data_term_prefix', var)

    assert stub_controller.setting_calls[-1] == ('source', 'data_term_prefix', 'x')
    assert var.get() == 'prev'
    assert window._error_var.get() == 'bad prefix'


def test_source_option_change_success_updates_previous_value(window, stub_controller):
    window._error_var.set('old error')

    window._on_source_option_changed('technical_fields', 4)

    assert stub_controller.setting_calls[-1] == ('source', 'technical_fields', 4)
    assert window._prev_source['technical_fields'] == 4
    assert window._error_var.get() == ''


def test_source_option_change_failure_keeps_previous_value(window, stub_controller):
    stub_controller.setting_response = ConfigSetResponse(success=False, error='bad option')
    original = window._prev_source['technical_fields']

    window._on_source_option_changed('technical_fields', 5)

    assert stub_controller.setting_calls[-1] == ('source', 'technical_fields', 5)
    assert window._prev_source['technical_fields'] == original
    assert window._error_var.get() == 'bad option'


def test_target_entry_change_success_updates_previous_value(window, stub_controller):
    var = window._target_vars['schema']
    var.set('reporting')

    window._on_target_entry_changed('schema', var)

    assert stub_controller.setting_calls[-1] == ('target', 'schema', 'reporting')
    assert window._prev_target['schema'] == 'reporting'
    assert window._error_var.get() == ''


def test_target_entry_change_failure_reverts_value(window, stub_controller):
    stub_controller.setting_response = ConfigSetResponse(success=False, error='bad schema')
    window._prev_target['schema'] = 'public'
    var = window._target_vars['schema']
    var.set('x')

    window._on_target_entry_changed('schema', var)

    assert stub_controller.setting_calls[-1] == ('target', 'schema', 'x')
    assert var.get() == 'public'
    assert window._error_var.get() == 'bad schema'


def test_on_back_calls_controller(window, stub_controller):
    window._on_back()
    stub_controller.show_adapter_selection.assert_called_once_with()


def test_on_translate_clears_error_calls_controller_and_reenables_button(window, stub_controller):
    window._error_var.set('old error')

    window._on_translate()

    stub_controller.on_translate.assert_called_once_with()
    assert window._error_var.get() == ''
    assert 'disabled' not in window._translate_btn.state()


def test_on_translate_ignores_tclerror_when_button_reenable_fails(window, stub_controller):
    button = MagicMock()
    button.state.side_effect = [None, tk.TclError('widget destroyed')]
    window._translate_btn = button

    window._on_translate()

    assert button.state.call_count == 2
    stub_controller.on_translate.assert_called_once_with()


def test_show_error_sets_error_text(window):
    window.show_error('inline error')
    assert window._error_var.get() == 'inline error'


def test_show_packs_frame(window):
    window.show()
    assert window.winfo_manager() == 'pack'