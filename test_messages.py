import pytest
from messages import (
    FileValidationRequest, FileValidationResponse,
    ConfigSetRequest, ConfigSetResponse,
    ReadinessRequest, ReadinessResponse,
    SchemaValidationRequest, SchemaValidationResponse,
    ProcessedGlossaryData,
    ProcessRequest, ProcessResponse,
    WriteOutputRequest, WriteOutputResponse,
)


# --- FileValidation ---

def test_file_validation_request_fields():
    req = FileValidationRequest(path='/some/path.csv', file_type='input')
    assert req.path == '/some/path.csv'
    assert req.file_type == 'input'


def test_file_validation_response_valid():
    resp = FileValidationResponse(valid=True, error=None)
    assert resp.valid is True
    assert resp.error is None


def test_file_validation_response_invalid():
    resp = FileValidationResponse(valid=False, error='File not found')
    assert resp.valid is False
    assert resp.error == 'File not found'


# --- ConfigSet ---

def test_config_set_request_fields():
    req = ConfigSetRequest(parameter='connection', value='mydb')
    assert req.parameter == 'connection'
    assert req.value == 'mydb'


def test_config_set_response_success():
    resp = ConfigSetResponse(success=True, error=None)
    assert resp.success is True


def test_config_set_response_failure():
    resp = ConfigSetResponse(success=False, error='bad value')
    assert resp.success is False
    assert 'bad value' in resp.error


# --- Readiness ---

def test_readiness_request_fields():
    req = ReadinessRequest(source_paths={'bg': '/a.csv'}, connection='conn')
    assert req.source_paths == {'bg': '/a.csv'}
    assert req.connection == 'conn'


def test_readiness_response_ready():
    resp = ReadinessResponse(ready=True, errors=[])
    assert resp.ready is True
    assert resp.errors == []


def test_readiness_response_not_ready():
    resp = ReadinessResponse(ready=False, errors=['missing connection'])
    assert resp.ready is False
    assert len(resp.errors) == 1


# --- SchemaValidation ---

def test_schema_validation_request_fields():
    req = SchemaValidationRequest(source_dfs={'key': None})
    assert 'key' in req.source_dfs


def test_schema_validation_response_valid():
    resp = SchemaValidationResponse(valid=True, errors=[])
    assert resp.valid is True


# --- ProcessedGlossaryData ---

def test_processed_glossary_data_fields():
    data = ProcessedGlossaryData(df_term='t', df_col_term_rel='c', df_term_rel='r')
    assert data.df_term == 't'
    assert data.df_col_term_rel == 'c'
    assert data.df_term_rel == 'r'


# --- Process ---

def test_process_request_fields():
    req = ProcessRequest(source_paths={}, source_adapter=None, target_adapter=None)
    assert req.source_paths == {}


def test_process_response_success():
    resp = ProcessResponse(success=True, errors=[], data='data')
    assert resp.success is True
    assert resp.data == 'data'


def test_process_response_failure():
    resp = ProcessResponse(success=False, errors=['err'], data=None)
    assert resp.success is False
    assert resp.data is None


# --- WriteOutput ---

def test_write_output_request_fields():
    req = WriteOutputRequest(data=None, target_paths={'terms': '/t.csv'}, target_adapter=None)
    assert req.target_paths == {'terms': '/t.csv'}


def test_write_output_response_success():
    resp = WriteOutputResponse(success=True, errors=[], output_files=['/t.csv'])
    assert resp.success is True
    assert resp.output_files == ['/t.csv']


def test_write_output_response_failure():
    resp = WriteOutputResponse(success=False, errors=['write error'], output_files=[])
    assert resp.success is False
    assert resp.output_files == []


# --- Immutability (named tuples are immutable) ---

def test_namedtuple_immutable():
    req = FileValidationRequest(path='/a.csv', file_type='input')
    with pytest.raises(AttributeError):
        req.path = '/b.csv'
