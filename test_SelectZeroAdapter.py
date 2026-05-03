import pytest
from adapters import SelectZeroAdapter
from messages import ConfigSetRequest


@pytest.fixture
def sz():
    return SelectZeroAdapter()


# --- required_target_files ---

def test_required_target_files(sz):
    assert set(sz.required_target_files.keys()) == {'terms', 'col_term_rel', 'term_rel'}


# --- output_columns ---

def test_output_columns_terms(sz):
    assert sz.output_columns('terms') == ['name', 'color', 'description', 'type', 'domain', 'owner']


def test_output_columns_col_term_rel(sz):
    assert sz.output_columns('col_term_rel') == ['connection', 'schema', 'object', 'column', 'term']


def test_output_columns_term_rel(sz):
    assert sz.output_columns('term_rel') == ['sourceName', 'relation', 'targetName']


def test_output_columns_unknown_key(sz):
    assert sz.output_columns('unknown') == []


# --- get_config / set_config ---

def test_default_config(sz):
    cfg = sz.get_config()
    assert cfg['connection'] == ''
    assert cfg['schema'] == 'public'
    assert cfg['owner'] == ''
    assert cfg['color'] == ''


def test_set_connection_valid(sz):
    resp = sz.set_config(ConfigSetRequest('connection', 'mydb'))
    assert resp.success is True
    assert sz.get_config()['connection'] == 'mydb'


def test_set_connection_too_short(sz):
    resp = sz.set_config(ConfigSetRequest('connection', 'x'))
    assert resp.success is False


def test_set_color_empty(sz):
    resp = sz.set_config(ConfigSetRequest('color', ''))
    assert resp.success is True


def test_set_color_too_long(sz):
    resp = sz.set_config(ConfigSetRequest('color', 'x' * 41))
    assert resp.success is False


def test_set_unknown_param(sz):
    resp = sz.set_config(ConfigSetRequest('nonexistent', 'val'))
    assert resp.success is False
