import translator
import pytest

@pytest.fixture
def translator_obj():
    return translator.Translator()

def test_file_adding(translator_obj, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_arisonastik.csv')
    translator_obj.set_input_file("business")
    assert translator_obj.business_glossary == r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_arisonastik.csv'