import translator
import pytest

@pytest.fixture
def translator_obj():
    return translator.Translator()

def test_file_adding(translator_obj, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_arisonastik.csv')
    translator_obj.set_input_file("business")
    assert translator_obj.business_glossary == r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_arisonastik.csv'

# def test_settings(translator_obj, monkeypatch):

#Test TODO:
#           1) output file name doesn't have .csv extension
#           2) output file folder doesn't exist
#           3) output file naming is correct
#           4) setting term add-ons works correctly
#           5) if addon is shorter, error message should be returned
#           6) if addon is longer, error message should be returned
#           7) navigation around the menu
#           8) option setting works correctly
#           9) option setting rejects illegal input
#           10) confirm that duplicate file name detection works in is_ready_for_translation
#           11) confirm that detecting empty file names works in is_ready_for_translation