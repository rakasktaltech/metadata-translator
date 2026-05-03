import translator
from translator import validate_dataframes as validate
import pandas as pd
import pytest
from io import StringIO

@pytest.fixture
def test_bg_pd():
    csv_data = """MÕISTE_ET;SEOSE TÜÜP;SEOTUD MÕISTE;MÄÄRATLUS VÕI SELGITUS_ET
aadressiandmed;SEOTUD;kontaktandmed;
administraator;SEOTUD;administraator;
akordionvalik;SEOTUD;taotlused;valikugruppide haldamise süsteem
allkirjastaja;SEOTUD;allkirjastaja;allkirja (sh digiallkirja) andmine isiku poolt, kellel on esindamisõigus
allkirjastamisõigus;SEOTUD;allkirjastamisõigus;seaduslik või volitatud esindamine
aruanne;KUULUB GRUPPI;taotlus/leping/aruanne;eralduse saaja on kohustatud esitama aruande projekti-, tegevustoetuse ning loometöötasu eesmärgi teostumise – tegelikult saadud tulude ja tehtud kulutuste kohta 60 kalendripäeva jooksul peale projekti teostumist või tegevustoetust saanud perioodi lõppemist. Kultuurkapitali juhatajal on õigus omal algatusel või eralduse saaja avalduse alusel aruande esitamise tähtaega mõjuvatel põhjustel muuta, lähtudes haldusmenetluse seaduses sätestatust. Mitteresidendist eralduse saaja ei ole kohustatud esitama aruannet, kui ekspertkomisjoni otsusega makstakse eraldus välja peale eesmärgi täitumist.
asutus;SEOTUD;kontaktandmed/allkirjastaja;halduslikke, kultuurilisi, hariduslikke vm ülesandeid täitev iseseisev, ainelise tootmisega mitte tegelev organ, institutsioon.
ekspert;KUULUB GRUPPI;ekspert;valdkonna asjatundja eriteadmisi nõudvate otsuste tegemiseks
eralduse tagasimaksmine;SEOTUD;toetuse tagasimaksmine;"eralduse saajal on kohustus tagastada eraldus 10 tööpäeva jooksul alates Kultuurkapitalilt kirjaliku tagasinõude otsuse saamisest. Tagasimaksmisele kuuluva eralduse, mis on suurem kui 50 eurot, võib ajatada eralduse saaja põhjendatud avalduse alusel kuni 12 kuuks, kui korraga maksmine seab eralduse saaja olulisel määral makseraskustesse või esinevad muud kaalukad asjaolud. Kui eralduse saaja ei maksa ajatamiskava kohaselt eraldust tagasi, jääb eralduse saaja Kultuurkapitali ees võlglaseks."
eraldusotsus;KUULUB GRUPPI;taotlus/leping/aruanne;taotlus rahuldatakse sisulise hindamise alusel kas täielikult või osaliselt või jäetakse taotlus rahuldamata (edaspidi ühiselt nimetatud eraldusotsus). Eraldusotsuste tegemisel lähtutakse laekunud taotluste analüüsist ning jagamisele kinnitatud rahalistest vahenditest. Kui raha jagamise korras on sätestatud eralduste kindel arv või suurus, lähtutakse otsuse tegemisel vastavatest tingimustest."""
    df = pd.read_csv(StringIO(csv_data), delimiter=";", encoding='utf-8')
    return df

@pytest.fixture
def test_dg_pd():
    csv_data = """ÄRISÕNASTIKU TERMIN;ANDMESÕNASTIKU TERMIN;Tabeli nimi;Välja nimi;Kommentaarid;KOOSTAMISE MÄRKUSED
    kasutajakonto: kirje;kirje unikaalne identifikaator;accounts;id;primery key;tehniline tunnus
    kasutajakonto;;accounts;user_id;seos users.id;Tehniline tunnus
    kasutajakonto;;accounts;account_name;taotleja nimetus;Kas siin tabelis on ainult taotlejate kasutajakontote andmed? Kuna allpool on jah/ei väli selle kohta, siis tekkis kahtlus.
    kasutajakonto;konto omaniku kontotüüp;accounts;account_type;kontotüüp: 1 - eraisik, 2 - juriidiline isik, 3 -Riigi- või avaliku sektori asutus, 4 - Välismaa juriidiline isik;
    kasutajakonto;taotleja konto kustutamise märge;accounts;is_deleted;kustutatud: 1 - jah, 0 - ei;ei ole kasutuses
    kasutajakonto;kasutajakonto loomise kuupäev;;created;loomise kuupäev;tehniline tunnus
    kasutajakonto;kasutajakonto loomise kuupäev;accounts;;loomise kuupäev;tehniline tunnus
    kasutajakonto;kasutajakonto loomise kuupäev;accounts;created;;tehniline tunnus
    ;kasutajakonto loomise kuupäev;accounts;created;loomise kuupäev;tehniline tunnus
    kasutajakonto;kasutajakonto loomise kuupäev;accounts;created;loomise kuupäev;tehniline tunnus
    kasutajakonto;kasutajakonto muutmise kuupäev;accounts;modified;muutmise kuupäev;tehniline tunnus
    kasutajakonto;seos legent.id (seos jur isikuga);accounts;legent_id;seos legent.id;tehniline tunnus: ei ole kasutuses
    kasutajakonto;kasutajakonto allkirjastamise õigus;accounts;is_signer;allkirjastaja: 1 - jah, 0 - ei;
    kasutajakonto;kasutajakonto taotluse esitamise õigus;accounts;is_applicant;taotleja: 1 - jah, 0 - ei;
    kirje;kirje unikaalne identifikaator;applications;id;primery key;tehniline tunnus"""
    df = pd.read_csv(StringIO(csv_data), delimiter=";", encoding='utf-8')
    return df

def test_validate1(test_bg_pd, test_dg_pd):
    assert validate(test_bg_pd, test_dg_pd) == "", "Assert that validation passes if all requirements are met"

def test_validate2():
    bg_columns = ["MÕISTE_ET", "SEOSE TÜÜP", "SEOTUD MÕISTE", "MÄÄRATLUS VÕI SELGITUS_ET"]
    dg_columns = ["ÄRISÕNASTIKU TERMIN", "ANDMESÕNASTIKU TERMIN", "Välja nimi", "Kommentaarid", "KOOSTAMISE MÄRKUSED"]
    bg_df = pd.DataFrame(columns=bg_columns)
    dg_df = pd.DataFrame(columns=dg_columns)
    assert validate(bg_df, dg_df) == "Missing required columns from data glossary: ['Tabeli nimi']", "Assert that validation catches missing columns"

def test_validate3():
    bg_columns = ["MÕISTE_ET", "SEOTUD MÕISTE", "MÄÄRATLUS VÕI SELGITUS_ET"]
    dg_columns = ["ÄRISÕNASTIKU TERMIN", "ANDMESÕNASTIKU TERMIN", "Tabeli nimi", "Välja nimi", "Kommentaarid", "KOOSTAMISE MÄRKUSED"]
    bg_df = pd.DataFrame(columns=bg_columns)
    dg_df = pd.DataFrame(columns=dg_columns)
    assert validate(bg_df, dg_df) == "Missing required columns from business glossary: ['SEOSE TÜÜP']", "Assert that validation catches missing columns"

@pytest.fixture
def test_vanilla_translator(test_bg_pd, test_dg_pd):
    transl = translator.Translator()
    transl.df_bg = test_bg_pd
    transl.df_dg = test_dg_pd
    transl.connection = "kala"
    transl.owner = "Kamm Kala"
    return transl

def test_translator_prefix(test_vanilla_translator):
    transl = test_vanilla_translator
    transl.data_term_prefix = "321_"
    transl.business_term_prefix = "123_"
    transl.resolve_business_glossary()
    transl.resolve_data_glossary()
    concept_row = transl.df_term.loc[transl.df_term['name'] == '123_allkirjastamisõigus'].iloc[0]
    data_row = transl.df_term.loc[transl.df_term['name'] == '321_kasutajakonto loomise kuupäev'].iloc[0]

    assert concept_row.tolist() == ['123_allkirjastamisõigus', '', 'seaduslik või volitatud esindamine', 'Concept', '', 'Kamm Kala']
    assert data_row.tolist() == ['321_kasutajakonto loomise kuupäev', '', 'loomise kuupäev // tehniline tunnus', 'Term', '', 'Kamm Kala']


def test_validate_reports_both_business_and_data_glossary_problems():
    bg_df = pd.DataFrame(columns=['MÕISTE_ET'])
    dg_df = pd.DataFrame(columns=['ÄRISÕNASTIKU TERMIN'])

    message = validate(bg_df, dg_df)

    assert "Missing required columns from business glossary" in message
    assert "Missing required columns from data glossary" in message


def test_is_unused_matches_case_insensitively():
    assert translator.is_unused('See väli EI OLE KASUTUSES praegu') is not None


def test_is_technical_field_matches_case_insensitively():
    assert translator.is_technical_field('märkus: Tehniline Tunnus süsteemi jaoks') is not None


def test_is_ready_for_translation_fails_for_duplicate_paths(test_vanilla_translator):
    transl = test_vanilla_translator
    transl.term_output_file = transl.business_glossary

    assert transl.is_ready_for_translation() is False


def test_get_term_name_appends_numeric_suffix_for_duplicates(test_vanilla_translator):
    transl = test_vanilla_translator

    first = transl.get_term_name('dupe term')
    second = transl.get_term_name('dupe term')

    assert first == 'dupe term'
    assert second == 'dupe term_2'

