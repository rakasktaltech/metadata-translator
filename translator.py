import os
import csv
import re

import pandas as pd
from shutil import ReadError

def is_correct_input(file_name):
    # Check if the path is absolute and file exists
    if not os.path.isabs(file_name) or not os.path.isfile(file_name):
        print("No such file found! Try again!")
        return False

    # Check for .csv extension
    if not file_name.lower().endswith('.csv'):
        print("It has to be a .csv file! Try another file!")
        return False

    # Try reading the file as a CSV with ';' delimiter
    try:
        with open(file_name, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            first_row = next(reader, None)
            if first_row is None or len(first_row) < 1:
                return False
    except (OSError, UnicodeDecodeError, csv.Error):
        print("Could not verify the files contents as suitable! Try another file!")
        return False

    csvfile.close()
    return True

def is_correct_output(destination):
    # Check if file has a .csv extension
    if not destination.lower().endswith('.csv'):
        print("Error: Output file must be a .csv file.")
        return False

    # Extract the directory from the path
    directory = os.path.dirname(destination)

    # Check if the directory exists
    if not os.path.isdir(directory):
        print("Error: The directory does not exist.")
        return False

    # Check if the file already exists
    if os.path.exists(destination):
        print("Error: File already exists. Overwriting is not allowed.")
        return False

    return True

def validate_dataframes(df_bg, df_dg):
    missing_bg_terms = []
    missing_dg_terms = []
    answer = ""
    if "MÕISTE_ET" not in df_bg.columns:
        missing_bg_terms.append("MÕISTE_ET")
    if "SEOTUD MÕISTE" not in df_bg.columns:
        missing_bg_terms.append("SEOTUD MÕISTE")
    if "MÄÄRATLUS VÕI SELGITUS_ET" not in df_bg.columns:
        missing_bg_terms.append("MÄÄRATLUS VÕI SELGITUS_ET")
    if "SEOSE TÜÜP" not in df_bg.columns:
        missing_bg_terms.append("SEOSE TÜÜP")
    if "ANDMESÕNASTIKU TERMIN" not in df_dg.columns:
        missing_dg_terms.append("ANDMESÕNASTIKU TERMIN")
    if "KOOSTAMISE MÄRKUSED" not in df_dg.columns:
        missing_dg_terms.append("KOOSTAMISE MÄRKUSED")
    if "Kommentaarid" not in df_dg.columns:
        missing_dg_terms.append("Kommentaarid")
    if "Tabeli nimi" not in df_dg.columns:
        missing_dg_terms.append("Tabeli nimi")
    if "Välja nimi" not in df_dg.columns:
        missing_dg_terms.append("Välja nimi")

    if missing_bg_terms:
        answer += "Missing required columns from business glossary:" + str(missing_bg_terms)
    if missing_dg_terms:
        answer += "Missing required columns from data glossary:" + str(missing_dg_terms)
    return answer

def is_unused(txt: str):
    return re.search(r"ei ole kasutuses", txt, re.IGNORECASE)

def is_technical_field(txt: str):
    return re.search(r"tehniline tunnus", txt, re.IGNORECASE)


class Translator:
    data_term_duplicate_options = {1: "Duplicate field data term empty after first occurrence noted as ''.",
                                   2: "Add iterated number as suffix to data term",
                                   3: "Leave duplicates in unchanged as duplicate data terms",
                                   4: "Exclude duplicates after first occurance"}
    data_term_duplicate = 2
    data_term_description_options = {1: "Database commentary",
                                     2: "Data glossary compiler commentary",
                                     3: "Database + compiler commentary",
                                     4: "Leave empty"}
    data_term_description = 3
    handle_technical_fields_options = {1: "Include technical and unused fields",
                                       2: "Exclude technical and unused fields",
                                       3: "Include technical, exclude unused",
                                       4: "Include unused, exclude technical"}
    technical_fields = 1
    data_term_prefix = ""
    data_term_suffix = ""
    business_term_prefix = ""
    business_term_suffix = ""
    term_relation_output_file = r'C:\Users\Administrator\Translator\btr_test.csv'
    term_output_file = r'C:\Users\Administrator\Translator\term_test.csv'
    column_term_relation_output_file = r'C:\Users\Administrator\Translator\col_term_rel_test.csv'
    connection = "not specified"
    owner = ""
    color = "red"
    schema = "public"

    # Specify structure of output files
    columns_term = ['name', 'color', 'description', 'type', 'domain', 'owner']
    columns_col_term_rel = ['connection', 'schema', 'object', 'column', 'term']
    columns_term_rel = ['sourceName', 'relation', 'targetName']

    # Create dataframes for output
    df_term = pd.DataFrame(columns=columns_term)
    df_col_term_rel = pd.DataFrame(columns=columns_col_term_rel)
    df_term_rel = pd.DataFrame(columns=columns_term_rel)
    df_bg = pd.DataFrame()
    df_dg = pd.DataFrame()
    duplicates_dict = {}

    def __init__(self):
        self.business_glossary = r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_business_glossary.csv'
        self.data_glossary = r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_data_glossary.csv'

    def is_ready_for_translation(self):
        file_attributes = [self.business_glossary, self.data_glossary, self.term_output_file, self.column_term_relation_output_file, self.term_relation_output_file]

        if ("none" in file_attributes) | ("" in file_attributes):
            print('One or more file name attribute missing, set them in the setting menu')
            return False
        if len(set(file_attributes)) != 5:
            print('Duplicate names detected in file names, please change them in settings menu')
            return False
        if self.connection == "not specified":
            print('Connection name not specified. Please provide a connection name')
            return False

        return True

    def set_input_file(self, file_type):
        destination = input(f"Insert {file_type} glossary .csv files' absolute address:")
        if not is_correct_input(destination):
            pass
        elif file_type == "business":
            self.business_glossary = destination
        elif file_type == "data":
            self.data_glossary = destination

    def set_output_file(self, file_type):
        destination = input(f"Insert {file_type} output .csv files' absolute address:")
        if not is_correct_output(destination):
            pass
        elif file_type == "terms":
            self.term_output_file = destination
        elif file_type == "business term relation":
            self.term_relation_output_file = destination
        elif file_type == "object term relation":
            self.column_term_relation_output_file = destination
        print("")

    def set_addon(self, term_type, addon_type):
        addon = input(f'Insert {term_type} term {addon_type}: ')
        if (len(addon) < 9) & (len(addon) > 1):
            if (term_type == "data") & (addon_type =="prefix"):
                self.data_term_prefix = addon
            if (term_type == "data") & (addon_type == "suffix"):
                self.data_term_suffix = addon
            if (term_type == "business") & (addon_type =="prefix"):
                self.business_term_prefix = addon
            if (term_type == "business") & (addon_type == "suffix"):
                self.business_term_suffix = addon
            print("")
        else:
            print("\n" * 50)
            print("Add-on length must be between 2 and 8 characters. Try again")

    def set_option(self, option_category):
        print("\n" * 50)
        while True:
            if option_category == "duplication":
                print("Data term duplication options:")
                for key, value in self.data_term_duplicate_options.items():
                    print(f'{key}) {value}')
                print(f'Current selection: {self.data_term_duplicate}) {self.data_term_duplicate_options[self.data_term_duplicate]}')
            elif option_category == "description":
                print("Data term description options:")
                for key, value in self.data_term_description_options.items():
                    print(f'{key}) {value}')
                print(f'Current selection: {self.data_term_description}) {self.data_term_description_options[self.data_term_description]}')
            elif option_category == "technical":
                print("Technical and unused field options:")
                for key, value in self.handle_technical_fields_options.items():
                    print(f'{key}) {value}')
                print(
                    f'Current selection: {self.technical_fields}) {self.handle_technical_fields_options[self.technical_fields]}')

            selection = input("Enter selected category: ")

            if selection in ["1", "2", "3", "4"]:
                if option_category == "duplication":
                    self.data_term_duplicate = int(selection)
                if option_category == "description":
                    self.data_term_description = int(selection)
                if option_category == "technical":
                    self.technical_fields = int(selection)
                print("Selection completed!")
                return
            else:
                print("Illegal selection, try again!")

    def set_parameter(self, parameter):
        answer = input(f"Insert {parameter} name: ")
        if len(answer) < 2:
            print("Input too short, must be at least 2 characters long")
            return
        if len(answer) > 40:
            print("Input too long, please provide a parameter under 40 characters")
            return
        if parameter == "connection":
            self.connection = answer
        if parameter == "owner":
            self.owner = answer
        if parameter == "schema":
            self.schema = answer

    def get_term_name(self, raw_term):
        base_term_name = self.data_term_prefix + raw_term + self.data_term_suffix
        term_name = ""

        # Track duplicates by raw term only
        if raw_term in self.duplicates_dict:
            self.duplicates_dict[raw_term] += 1
            if self.data_term_duplicate == 1:
                return term_name
            if self.data_term_duplicate == 2:
                term_name = f"{base_term_name}_{self.duplicates_dict[raw_term]}"
            if self.data_term_duplicate == 3:
                term_name = base_term_name
        else:
            self.duplicates_dict[raw_term] = 1
            term_name = base_term_name
        return term_name

    def resolve_data_glossary(self):
        self.duplicates_dict = {}
        for index, row in self.df_dg.iterrows():
            # Resolve duplicate term name entry resolution option selection

            if pd.isna(row['ANDMESÕNASTIKU TERMIN']) or pd.isnull(row['ANDMESÕNASTIKU TERMIN']):
                continue

            # Use raw term for duplication tracking
            raw_term = str(row['ANDMESÕNASTIKU TERMIN']).strip() if row['ANDMESÕNASTIKU TERMIN'] else ""
            term_name = self.get_term_name(raw_term)

            # Check for option to exclude duplicate fields after first occurence
            if (self.duplicates_dict[raw_term] > 1) and (self.data_term_duplicate == 4):
                continue

            # Resolve technical field inclusion option selection
            if (self.technical_fields == 2) and (
                    is_technical_field(str(row['KOOSTAMISE MÄRKUSED'])) or is_unused(str(row['KOOSTAMISE MÄRKUSED']))):
                continue

            if (self.technical_fields == 3) and (is_unused(str(row['KOOSTAMISE MÄRKUSED']))):
                continue

            if (self.technical_fields == 4) and (is_technical_field(str(row['KOOSTAMISE MÄRKUSED']))):
                continue

            description = ""
            row_type = "Term"

            # Resolve description option selection
            match self.data_term_description:
                case 1:
                    description = str(row['Kommentaarid'])
                case 2:
                    description = str(row['KOOSTAMISE MÄRKUSED']) if str(row['KOOSTAMISE MÄRKUSED']) else " "
                case 3:
                    if str(row['KOOSTAMISE MÄRKUSED']):
                        description = str(row['Kommentaarid']) + " // " + str(row['KOOSTAMISE MÄRKUSED'])
                case 4:
                    description = ""

            term_row = pd.DataFrame([{
                'name': term_name,
                'color': self.color,
                'description': description,
                'type': row_type,
                'domain': "",
                'owner': self.owner
            }])

            self.df_term = pd.concat([self.df_term, term_row], ignore_index=True)

            col_term_rel_row = pd.DataFrame([{
                'connection': self.connection,
                'schema': self.schema,
                'object': str(row['Tabeli nimi']),
                'column': str(row['Välja nimi']),
                'term': term_name
            }])

            self.df_col_term_rel = pd.concat([self.df_col_term_rel, col_term_rel_row], ignore_index=True)

            if pd.isna(row['ÄRISÕNASTIKU TERMIN']) or pd.isnull(row['ÄRISÕNASTIKU TERMIN']):
                continue

            #Resolve business term list and create term relations
            source_term_list = str(row['ÄRISÕNASTIKU TERMIN']).split(':')

            for source_term in source_term_list:
                st = str(source_term).strip()
                term_relation_row = pd.DataFrame([{
                    'sourceName': self.data_term_prefix + st + self.data_term_suffix,
                    'relation': "Related to",
                    'targetName': term_name
                }])

                self.df_term_rel = pd.concat([self.df_term_rel, term_relation_row], ignore_index=True)

    def resolve_business_glossary(self):
        for index, row in self.df_bg.iterrows():
            row_type = "Concept"

            term_name = self.business_term_prefix + str(row['MÕISTE_ET']) + self.business_term_suffix
            target_name = self.business_term_prefix + str(row['SEOTUD MÕISTE']) + self.business_term_suffix
            term_list = []

            if str(row['MÕISTE_ET']) not in term_list:
                term_list.append(str(row['MÕISTE_ET']))
                term_row = pd.DataFrame([{
                    'name': term_name,
                    'color': self.color,
                    'description': str(row['MÄÄRATLUS VÕI SELGITUS_ET']),
                    'type': row_type,
                    'domain': "",
                    'owner': self.owner
                }])

                self.df_term = pd.concat([self.df_term, term_row], ignore_index=True)

            if pd.notna(row['SEOTUD MÕISTE']) and str(row['SEOTUD MÕISTE']).strip() != "" and pd.notna(
                    row['SEOSE TÜÜP']):
                continue

            match str(row['SEOSE TÜÜP']):
                case "KUULUB GRUPPI":
                    relation = "Belongs to group"
                case "SEOTUD":
                    relation = "Related to"
                case "LAIEM":
                    relation = "Child of"
                case "KITSAM":
                    relation = "Parent of"
                case _:
                    relation = str(row['SEOSE TÜÜP']) if pd.notna(row['SEOSE TÜÜP']) else ""

            if row['SEOSE TÜÜP']:
                term_relation_row = pd.DataFrame([{
                    'sourceName': term_name,
                    'relation': relation,
                    'targetName': target_name
                }])

                self.df_term_rel = pd.concat([self.df_term_rel, term_relation_row], ignore_index=True)

    def translate(self):
        if not self.is_ready_for_translation():
            print('Translation aborted')
            return

        try:
            self.df_bg = pd.read_csv(self.business_glossary, delimiter=';', encoding='utf-8')
            self.df_dg = pd.read_csv(self.data_glossary, delimiter=';', encoding='utf-8')
        except ReadError:
            print('Unable to read file, aborting translation')
            return

        error_msg = validate_dataframes(self.df_bg, self.df_dg)

        if error_msg:
            print(error_msg)
            return

        self.resolve_data_glossary()
        self.resolve_business_glossary()

        #Resolve output files
        self.df_term.to_csv(self.term_output_file, index=False, sep=';', encoding='utf-8')
        self.df_col_term_rel.to_csv(self.column_term_relation_output_file, index=False, sep=';', encoding='utf-8')
        self.df_term_rel.to_csv(self.term_relation_output_file, index=False, sep=';', encoding='utf-8')

        print("\n" * 50)
        print("Translation successful, files ready for use!")