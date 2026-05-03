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


def test_process_sources_deduplicates_business_terms_and_keeps_relations(sa):
    df_bg = pd.DataFrame([
        {
            'MÕISTE_ET': 'Alpha',
            'SEOSE TÜÜP': 'SEOTUD',
            'SEOTUD MÕISTE': 'Beta',
            'MÄÄRATLUS VÕI SELGITUS_ET': 'first description',
        },
        {
            'MÕISTE_ET': 'Alpha',
            'SEOSE TÜÜP': pd.NA,
            'SEOTUD MÕISTE': pd.NA,
            'MÄÄRATLUS VÕI SELGITUS_ET': 'duplicate description',
        },
    ])
    df_dg = pd.DataFrame(columns=['ÄRISÕNASTIKU TERMIN', 'ANDMESÕNASTIKU TERMIN',
                                  'Tabeli nimi', 'Välja nimi', 'Kommentaarid', 'KOOSTAMISE MÄRKUSED'])

    data = sa.process_sources({'business_glossary': df_bg, 'data_glossary': df_dg})

    concept_rows = data.df_term[data.df_term['type'] == 'Concept']
    assert concept_rows['name'].tolist() == ['alpha']
    assert data.df_term_rel.to_dict('records') == [{
        'sourceName': 'alpha',
        'relation': 'Related to',
        'targetName': 'beta',
    }]


def test_process_sources_duplicate_option_one_blanks_later_duplicate_names(sa):
    sa.set_config(ConfigSetRequest('data_term_duplicate', 1))
    df_bg = pd.DataFrame(columns=['MÕISTE_ET', 'SEOSE TÜÜP', 'SEOTUD MÕISTE', 'MÄÄRATLUS VÕI SELGITUS_ET'])
    df_dg = pd.DataFrame([
        {
            'ÄRISÕNASTIKU TERMIN': pd.NA,
            'ANDMESÕNASTIKU TERMIN': 'Dupe',
            'Tabeli nimi': 'tbl',
            'Välja nimi': 'col1',
            'Kommentaarid': 'c1',
            'KOOSTAMISE MÄRKUSED': 'n1',
        },
        {
            'ÄRISÕNASTIKU TERMIN': pd.NA,
            'ANDMESÕNASTIKU TERMIN': 'Dupe',
            'Tabeli nimi': 'tbl',
            'Välja nimi': 'col2',
            'Kommentaarid': 'c2',
            'KOOSTAMISE MÄRKUSED': 'n2',
        },
    ])

    data = sa.process_sources({'business_glossary': df_bg, 'data_glossary': df_dg})

    assert data.df_term['name'].tolist() == ['dupe', '']


def test_process_sources_duplicate_option_four_skips_later_duplicate_rows(sa):
    sa.set_config(ConfigSetRequest('data_term_duplicate', 4))
    df_bg = pd.DataFrame(columns=['MÕISTE_ET', 'SEOSE TÜÜP', 'SEOTUD MÕISTE', 'MÄÄRATLUS VÕI SELGITUS_ET'])
    df_dg = pd.DataFrame([
        {
            'ÄRISÕNASTIKU TERMIN': pd.NA,
            'ANDMESÕNASTIKU TERMIN': 'Dupe',
            'Tabeli nimi': 'tbl',
            'Välja nimi': 'col1',
            'Kommentaarid': 'c1',
            'KOOSTAMISE MÄRKUSED': 'n1',
        },
        {
            'ÄRISÕNASTIKU TERMIN': pd.NA,
            'ANDMESÕNASTIKU TERMIN': 'Dupe',
            'Tabeli nimi': 'tbl',
            'Välja nimi': 'col2',
            'Kommentaarid': 'c2',
            'KOOSTAMISE MÄRKUSED': 'n2',
        },
    ])

    data = sa.process_sources({'business_glossary': df_bg, 'data_glossary': df_dg})

    assert data.df_term['name'].tolist() == ['dupe']
    assert data.df_col_term_rel['column'].tolist() == ['col1']


def test_process_sources_description_option_one_uses_database_commentary(sa):
    sa.set_config(ConfigSetRequest('data_term_description', 1))
    df_bg = pd.DataFrame(columns=['MÕISTE_ET', 'SEOSE TÜÜP', 'SEOTUD MÕISTE', 'MÄÄRATLUS VÕI SELGITUS_ET'])
    df_dg = pd.DataFrame([
        {
            'ÄRISÕNASTIKU TERMIN': pd.NA,
            'ANDMESÕNASTIKU TERMIN': 'Term',
            'Tabeli nimi': 'tbl',
            'Välja nimi': 'col',
            'Kommentaarid': 'database comment',
            'KOOSTAMISE MÄRKUSED': 'author note',
        },
    ])

    data = sa.process_sources({'business_glossary': df_bg, 'data_glossary': df_dg})

    assert data.df_term.iloc[0]['description'] == 'database comment'


def test_process_sources_technical_option_two_filters_technical_and_unused(sa):
    sa.set_config(ConfigSetRequest('technical_fields', 2))
    df_bg = pd.DataFrame(columns=['MÕISTE_ET', 'SEOSE TÜÜP', 'SEOTUD MÕISTE', 'MÄÄRATLUS VÕI SELGITUS_ET'])
    df_dg = pd.DataFrame([
        {
            'ÄRISÕNASTIKU TERMIN': pd.NA,
            'ANDMESÕNASTIKU TERMIN': 'Tech Term',
            'Tabeli nimi': 'tbl',
            'Välja nimi': 'col1',
            'Kommentaarid': 'database comment',
            'KOOSTAMISE MÄRKUSED': 'tehniline tunnus',
        },
        {
            'ÄRISÕNASTIKU TERMIN': pd.NA,
            'ANDMESÕNASTIKU TERMIN': 'Unused Term',
            'Tabeli nimi': 'tbl',
            'Välja nimi': 'col2',
            'Kommentaarid': 'database comment',
            'KOOSTAMISE MÄRKUSED': 'ei ole kasutuses',
        },
        {
            'ÄRISÕNASTIKU TERMIN': pd.NA,
            'ANDMESÕNASTIKU TERMIN': 'Keep Term',
            'Tabeli nimi': 'tbl',
            'Välja nimi': 'col3',
            'Kommentaarid': 'database comment',
            'KOOSTAMISE MÄRKUSED': 'regular note',
        },
    ])

    data = sa.process_sources({'business_glossary': df_bg, 'data_glossary': df_dg})

    assert data.df_term['name'].tolist() == ['keep term']
    assert data.df_col_term_rel['column'].tolist() == ['col3']


def test_process_sources_skips_unknown_business_relation_types(sa):
    df_bg = pd.DataFrame([
        {
            'MÕISTE_ET': 'Alpha',
            'SEOSE TÜÜP': 'UNKNOWN',
            'SEOTUD MÕISTE': 'Beta',
            'MÄÄRATLUS VÕI SELGITUS_ET': 'description',
        },
    ])
    df_dg = pd.DataFrame(columns=['ÄRISÕNASTIKU TERMIN', 'ANDMESÕNASTIKU TERMIN',
                                  'Tabeli nimi', 'Välja nimi', 'Kommentaarid', 'KOOSTAMISE MÄRKUSED'])

    data = sa.process_sources({'business_glossary': df_bg, 'data_glossary': df_dg})

    assert data.df_term_rel.empty
