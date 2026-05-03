import os
import pytest
from adapters import SelectZeroAdapter, StatisticsEstoniaAdapter
from messages import FileValidationRequest, ProcessRequest, ReadinessRequest
from model import TranslationModel


WORKSPACE = os.path.dirname(os.path.abspath(__file__))
VALID_BG = os.path.join(WORKSPACE, 'test_business_glossary.csv')
VALID_DG = os.path.join(WORKSPACE, 'test_data_glossary.csv')


@pytest.fixture
def model():
    return TranslationModel()


# --- validate_input_file ---

def test_input_valid_csv(model):
    resp = model.validate_input_file(FileValidationRequest(VALID_BG, 'input'))
    assert resp.valid is True
    assert resp.error is None


def test_input_relative_path(model):
    resp = model.validate_input_file(FileValidationRequest('test_business_glossary.csv', 'input'))
    assert resp.valid is False
    assert 'absolute' in resp.error.lower()


def test_input_file_not_found(model):
    resp = model.validate_input_file(FileValidationRequest(
        os.path.join(WORKSPACE, 'nonexistent.csv'), 'input'))
    assert resp.valid is False
    assert 'not found' in resp.error.lower()


def test_input_wrong_extension(model, tmp_path):
    f = tmp_path / 'data.txt'
    f.write_text('a;b\n1;2\n', encoding='utf-8')
    resp = model.validate_input_file(FileValidationRequest(str(f), 'input'))
    assert resp.valid is False
    assert '.csv' in resp.error


def test_input_empty_csv(model, tmp_path):
    f = tmp_path / 'empty.csv'
    f.write_text('', encoding='utf-8')
    resp = model.validate_input_file(FileValidationRequest(str(f), 'input'))
    assert resp.valid is False


def test_input_non_utf8_file(model, tmp_path):
    f = tmp_path / 'bad.csv'
    f.write_bytes(b'\xff\xfe\x00not utf8')
    resp = model.validate_input_file(FileValidationRequest(str(f), 'input'))
    assert resp.valid is False


def test_input_valid_single_column_csv(model, tmp_path):
    f = tmp_path / 'single.csv'
    f.write_text('col\nval\n', encoding='utf-8')
    resp = model.validate_input_file(FileValidationRequest(str(f), 'input'))
    assert resp.valid is True


# --- validate_output_file ---

def test_output_valid_path(model, tmp_path):
    path = str(tmp_path / 'output.csv')
    resp = model.validate_output_file(FileValidationRequest(path, 'output'))
    assert resp.valid is True
    assert resp.error is None


def test_output_wrong_extension(model, tmp_path):
    path = str(tmp_path / 'output.txt')
    resp = model.validate_output_file(FileValidationRequest(path, 'output'))
    assert resp.valid is False
    assert '.csv' in resp.error


def test_output_directory_not_exist(model):
    path = r'C:\nonexistent_dir_xyz\output.csv'
    resp = model.validate_output_file(FileValidationRequest(path, 'output'))
    assert resp.valid is False
    assert 'directory' in resp.error.lower()


def test_output_file_already_exists(model):
    resp = model.validate_output_file(FileValidationRequest(VALID_BG, 'output'))
    assert resp.valid is False
    assert 'exists' in resp.error.lower()


def test_output_no_directory_component(model, tmp_path):
    # path with no directory part (just filename) — os.path.dirname returns ''
    # which passes the directory check; file must not exist
    os.chdir(tmp_path)
    resp = model.validate_output_file(FileValidationRequest('out.csv', 'output'))
    assert resp.valid is True


# --- Stage 2 readiness / process ---

def test_check_readiness_requires_connection_and_paths(model):
    resp = model.check_readiness(ReadinessRequest(
        source_paths={'business_glossary': VALID_BG, 'data_glossary': ''},
        connection='',
    ))
    assert resp.ready is False
    assert any('data_glossary' in error for error in resp.errors)
    assert any('Connection name is required' in error for error in resp.errors)


def test_process_success_returns_processed_data(model):
    req = ProcessRequest(
        source_paths={'business_glossary': VALID_BG, 'data_glossary': VALID_DG},
        source_adapter=StatisticsEstoniaAdapter(),
        target_adapter=SelectZeroAdapter(),
    )
    resp = model.process(req)
    assert resp.success is True
    assert resp.errors == []
    assert list(resp.data.df_term.columns) == ['name', 'color', 'description', 'type', 'domain', 'owner']
    assert list(resp.data.df_col_term_rel.columns) == ['connection', 'schema', 'object', 'column', 'term']
    assert list(resp.data.df_term_rel.columns) == ['sourceName', 'relation', 'targetName']
    assert not resp.data.df_term.empty


def test_process_returns_schema_errors(model, tmp_path):
    bad_bg = tmp_path / 'bad_business.csv'
    bad_bg.write_text('MÕISTE_ET\nterm\n', encoding='utf-8')

    req = ProcessRequest(
        source_paths={'business_glossary': str(bad_bg), 'data_glossary': VALID_DG},
        source_adapter=StatisticsEstoniaAdapter(),
        target_adapter=SelectZeroAdapter(),
    )
    resp = model.process(req)
    assert resp.success is False
    assert resp.data is None
    assert any('Missing required columns from Business Glossary' in error for error in resp.errors)
