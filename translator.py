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
    # TODO: Lisa kontroll, mis ütleks, kas kõik tõlkeks vajalikud read on dataframe's olemas
    pass


class Translator:

    data_term_duplicate_options = {1: "'null' after first occurrence",
                                   2: "Add iterated number as suffix",
                                   3: "Leave duplicates in"}
    data_term_duplicate = 2
    data_term_description_options = {1: "Database commentary",
                                     2: "Data glossary compiler commentary",
                                     3: "Database + compiler commentary"}
    data_term_description = 3
    handle_technical_fields_options = {1: "Include technical and unused fields",
                                       2: "Exclude technical and unused fields",
                                       3: "Include technical, exclude unused"}
    technical_fields = 1
    data_term_prefix = ""
    data_term_suffix = ""
    business_term_prefix = ""
    business_term_suffix = ""
    term_relation_output_file = r'C:\Users\Administrator\btr.csv'
    term_output_file = r'C:\Users\Administrator\term.csv'
    column_term_relation_output_file = r'C:\Users\Administrator\col_term_rel.csv'
    connection = "not specified"
    owner = ""
    color = "red"
    schema = "public" #

    def __init__(self):
        self.business_glossary = r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_arisonastik_short.csv'
        self.data_glossary = r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_andmekirjeldus_short.csv'

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
            if selection in ["1", "2", "3"]:
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
        if len(answer) > 40:
            print("Input too long, please provide a parameter under 40 characters")
            return
        if parameter == "connection":
            self.connection = answer
        if parameter == "owner":
            self.owner = answer
        if parameter == "schema":
            self.schema = answer

    def translate(self):
        if not self.is_ready_for_translation():
            print('Translation aborted')
            return

        try:
            df_bg = pd.read_csv(self.business_glossary, delimiter=';', encoding='utf-8')
            df_dg = pd.read_csv(self.data_glossary, delimiter=';', encoding='utf-8')
        except ReadError:
            print('Unable to read file, aborting translation')
            return

        validate_dataframes(df_bg, df_dg)

        #Specify structure of output files
        columns_term = ['name', 'color', 'description', 'type', 'domain', 'owner']
        columns_col_term_rel = ['connection', 'schema', 'object', 'column', 'term']
        columns_term_rel = ['sourceName', 'relation', 'targetName']

        #Create dataframes for output
        df_term = pd.DataFrame(columns = columns_term)
        df_col_term_rel = pd.DataFrame(columns = columns_col_term_rel)
        df_term_rel = pd.DataFrame(columns = columns_term_rel)
        duplicates_dict = {}

        #Loop over data glossary rows
        for index, row in df_dg.iterrows():
            #Resolve duplicate term name entry resolution option selection
            #todo: ADD LOGIC FOR OTHER MENU OPTIONS (nulling the term names and ignoring duplicates)

            if pd.isna(row['ANDMESÕNASTIKU TERMIN']) or pd.isnull(row['ANDMESÕNASTIKU TERMIN']):
                continue

            # Use raw term for duplication tracking
            raw_term = str(row['ANDMESÕNASTIKU TERMIN']).strip() if row['ANDMESÕNASTIKU TERMIN'] else ""
            term_name = ""
            base_term_name = self.data_term_prefix + raw_term + self.data_term_suffix

            # Track duplicates by raw term only
            if raw_term in duplicates_dict:
                duplicates_dict[raw_term] += 1
                if self.data_term_duplicate > 1:
                    term_name = f"{base_term_name}_{duplicates_dict[raw_term]}"
            else:
                duplicates_dict[raw_term] = 1
                term_name = base_term_name

            #Resolve technical field inclusion option selection
            if (
                    self.technical_fields == 2 and
                    (re.search(r"ei ole kasutuses", str(row['KOOSTAMISE MÄRKUSED']), re.IGNORECASE) or
                    re.search(r"tehniline tunnus", str(row['KOOSTAMISE MÄRKUSED']), re.IGNORECASE))
            ):
                continue

            if (
                    self.technical_fields == 3 and
                    re.search(r"ei ole kasutuses", str(row['KOOSTAMISE MÄRKUSED']), re.IGNORECASE)
            ):
                continue

            description = ""
            row_type = "Term"

            #Resolve description option selection
            match self.data_term_description:
                case 1:
                    description = str(row['Kommentaarid'])
                case 2:
                    description = str(row['KOOSTAMISE MÄRKUSED']) if str(row['KOOSTAMISE MÄRKUSED']) else " "
                case 3:
                    if str(row['KOOSTAMISE MÄRKUSED']):
                        description = str(row['Kommentaarid']) + " // " + str(row['KOOSTAMISE MÄRKUSED'])

            term_row = pd.DataFrame([{
                'name': term_name,
                'color': self.color,
                'description': description,
                'type': row_type,
                'domain': "",
                'owner': self.owner
            }])

            df_term = pd.concat([df_term, term_row], ignore_index=True)

            col_term_rel_row = pd.DataFrame([{
                'connection': self.connection,
                'schema': self.schema,
                'object': str(row['Tabeli nimi']),
                'column': str(row['Välja nimi']),
                'term': term_name
            }])

            df_col_term_rel = pd.concat([df_col_term_rel, col_term_rel_row], ignore_index=True)

            if pd.isna(row['ÄRISÕNASTIKU TERMIN']) or pd.isnull(row['ÄRISÕNASTIKU TERMIN']):
                continue

            source_term_list = str(row['ÄRISÕNASTIKU TERMIN']).split(':')
            for source_term in source_term_list:
                st = str(source_term).strip()
                term_relation_row = pd.DataFrame([{
                    'sourceName': self.data_term_prefix + st + self.data_term_suffix,
                    'relation': "Related to",
                    'targetName': term_name
                }])

                df_term_rel = pd.concat([df_term_rel, term_relation_row], ignore_index=True)

        #Loop over business glossary
        for index, row in df_bg.iterrows():
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

                df_term = pd.concat([df_term, term_row], ignore_index=True)

            if pd.notna(row['SEOTUD MÕISTE']) and str(row['SEOTUD MÕISTE']).strip() != "" and pd.notna(row['SEOSE TÜÜP']):
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

                df_term_rel = pd.concat([df_term_rel, term_relation_row], ignore_index=True)

        df_term.to_csv(self.term_output_file, index=False, sep=';', encoding='utf-8')
        df_col_term_rel.to_csv(self.column_term_relation_output_file, index=False, sep=';', encoding='utf-8')
        df_term_rel.to_csv(self.term_relation_output_file, index=False, sep=';', encoding='utf-8')

        print("\n" * 50)
        print("Translation successful, files ready for use!")