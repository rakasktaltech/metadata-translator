import pytest
import pandas as pd
from adapters import StatisticsEstoniaAdapter
from messages import ConfigSetRequest, SchemaValidationRequest


@pytest.fixture
def sa():
    return StatisticsEstoniaAdapter()


# --- required_source_files / required_columns ---

def test_required_source_files(sa):
    files = sa.required_source_files
    assert 'business_glossary' in files
    assert 'data_glossary' in files


def test_required_columns_business(sa):
    cols = sa.required_columns('business_glossary')
    assert 'MÕISTE_ET' in cols
    assert 'SEOSE TÜÜP' in cols


def test_required_columns_data(sa):
    cols = sa.required_columns('data_glossary')
    assert 'ANDMESÕNASTIKU TERMIN' in cols
    assert 'Tabeli nimi' in cols


def test_required_columns_unknown_key(sa):
    assert sa.required_columns('unknown') == []


# --- available_config_options ---

def test_config_options_keys(sa):
    opts = sa.available_config_options
    assert 'data_term_duplicate' in opts
    assert 'data_term_description' in opts
    assert 'technical_fields' in opts


def test_config_options_ranges(sa):
    for key, mapping in sa.available_config_options.items():
        assert set(mapping.keys()) == {1, 2, 3, 4}, f"{key} should have options 1-4"


# --- get_config / set_config ---

def test_default_config(sa):
    cfg = sa.get_config()
    assert cfg['data_term_prefix'] == ''
    assert cfg['data_term_duplicate'] == 2
    assert cfg['data_term_description'] == 3
    assert cfg['technical_fields'] == 1


def test_set_prefix_valid(sa):
    resp = sa.set_config(ConfigSetRequest('data_term_prefix', 'ab'))
    assert resp.success is True
    assert sa.get_config()['data_term_prefix'] == 'ab'


def test_set_prefix_empty_string(sa):
    resp = sa.set_config(ConfigSetRequest('data_term_suffix', ''))
    assert resp.success is True


def test_set_prefix_too_short(sa):
    resp = sa.set_config(ConfigSetRequest('data_term_prefix', 'x'))
    assert resp.success is False
    assert resp.error is not None


def test_set_prefix_too_long(sa):
    resp = sa.set_config(ConfigSetRequest('data_term_prefix', 'toolongval'))
    assert resp.success is False


def test_set_int_option_valid(sa):
    resp = sa.set_config(ConfigSetRequest('data_term_duplicate', 4))
    assert resp.success is True
    assert sa.get_config()['data_term_duplicate'] == 4


def test_set_int_option_out_of_range(sa):
    resp = sa.set_config(ConfigSetRequest('data_term_duplicate', 5))
    assert resp.success is False


def test_set_unknown_param(sa):
    resp = sa.set_config(ConfigSetRequest('nonexistent', 'val'))
    assert resp.success is False


# --- validate_schema ---

def test_validate_schema_valid(sa):
    df_bg = pd.DataFrame(columns=['MÕISTE_ET', 'SEOSE TÜÜP', 'SEOTUD MÕISTE', 'MÄÄRATLUS VÕI SELGITUS_ET'])
    df_dg = pd.DataFrame(columns=['ÄRISÕNASTIKU TERMIN', 'ANDMESÕNASTIKU TERMIN',
                                   'Tabeli nimi', 'Välja nimi', 'Kommentaarid', 'KOOSTAMISE MÄRKUSED'])
    resp = sa.validate_schema(SchemaValidationRequest({'business_glossary': df_bg, 'data_glossary': df_dg}))
    assert resp.valid is True
    assert resp.errors == []


def test_validate_schema_missing_columns(sa):
    df_bg = pd.DataFrame(columns=['MÕISTE_ET'])  # missing 3 columns
    df_dg = pd.DataFrame(columns=['ÄRISÕNASTIKU TERMIN', 'ANDMESÕNASTIKU TERMIN',
                                   'Tabeli nimi', 'Välja nimi', 'Kommentaarid', 'KOOSTAMISE MÄRKUSED'])
    resp = sa.validate_schema(SchemaValidationRequest({'business_glossary': df_bg, 'data_glossary': df_dg}))
    assert resp.valid is False
    assert any('Business Glossary' in e for e in resp.errors)


def test_validate_schema_missing_file_key(sa):
    df_dg = pd.DataFrame(columns=['ÄRISÕNASTIKU TERMIN', 'ANDMESÕNASTIKU TERMIN',
                                   'Tabeli nimi', 'Välja nimi', 'Kommentaarid', 'KOOSTAMISE MÄRKUSED'])
    resp = sa.validate_schema(SchemaValidationRequest({'data_glossary': df_dg}))  # no business_glossary key
    assert resp.valid is False
