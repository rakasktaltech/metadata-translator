import pytest
import pandas as pd
from adapters import SelectZeroAdapter
from messages import ConfigSetRequest
from messages import ProcessedGlossaryData


@pytest.fixture
def sz():
    return SelectZeroAdapter()


# --- required_target_files ---

def test_required_target_files(sz):
    assert set(sz.required_target_files.keys()) == {'terms', 'col_term_rel', 'term_rel'}


def test_required_source_files(sz):
    assert set(sz.required_source_files.keys()) == {'terms', 'col_term_rel', 'term_rel'}


# --- output_columns ---

def test_output_columns_terms(sz):
    assert sz.output_columns('terms') == ['name', 'color', 'description', 'type', 'domain', 'owner']


def test_output_columns_col_term_rel(sz):
    assert sz.output_columns('col_term_rel') == ['connection', 'schema', 'object', 'column', 'term']


def test_output_columns_term_rel(sz):
    assert sz.output_columns('term_rel') == ['sourceName', 'relation', 'targetName']


def test_output_columns_unknown_key(sz):
    assert sz.output_columns('unknown') == []


def test_available_config_options_empty(sz):
    assert sz.available_config_options == {}


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


def test_set_schema_valid(sz):
    resp = sz.set_config(ConfigSetRequest('schema', 'analytics'))
    assert resp.success is True
    assert sz.get_config()['schema'] == 'analytics'


def test_set_owner_too_long(sz):
    resp = sz.set_config(ConfigSetRequest('owner', 'x' * 41))
    assert resp.success is False


def test_set_color_empty(sz):
    resp = sz.set_config(ConfigSetRequest('color', ''))
    assert resp.success is True


def test_set_color_too_long(sz):
    resp = sz.set_config(ConfigSetRequest('color', 'x' * 41))
    assert resp.success is False


def test_set_color_max_length_is_valid(sz):
    color = 'x' * 40
    resp = sz.set_config(ConfigSetRequest('color', color))
    assert resp.success is True
    assert sz.get_config()['color'] == color


def test_set_unknown_param(sz):
    resp = sz.set_config(ConfigSetRequest('nonexistent', 'val'))
    assert resp.success is False


def test_write_output_writes_expected_csv_columns(sz, tmp_path):
    data = ProcessedGlossaryData(
        df_term=pd.DataFrame([{
            'name': 'term_a',
            'color': 'blue',
            'description': 'desc',
            'type': 'Term',
            'domain': '',
            'owner': 'owner_a',
        }]),
        df_col_term_rel=pd.DataFrame([{
            'connection': 'conn',
            'schema': 'public',
            'object': 'table_a',
            'column': 'column_a',
            'term': 'term_a',
        }]),
        df_term_rel=pd.DataFrame([{
            'sourceName': 'concept_a',
            'relation': 'Related to',
            'targetName': 'term_a',
        }]),
    )
    target_paths = {
        'terms': str(tmp_path / 'terms.csv'),
        'col_term_rel': str(tmp_path / 'col_term_rel.csv'),
        'term_rel': str(tmp_path / 'term_rel.csv'),
    }

    sz.write_output(data, target_paths)

    terms_df = pd.read_csv(target_paths['terms'], sep=';', encoding='utf-8')
    col_term_rel_df = pd.read_csv(target_paths['col_term_rel'], sep=';', encoding='utf-8')
    term_rel_df = pd.read_csv(target_paths['term_rel'], sep=';', encoding='utf-8')

    assert list(terms_df.columns) == sz.output_columns('terms')
    assert list(col_term_rel_df.columns) == sz.output_columns('col_term_rel')
    assert list(term_rel_df.columns) == sz.output_columns('term_rel')
    assert terms_df.iloc[0]['name'] == 'term_a'
