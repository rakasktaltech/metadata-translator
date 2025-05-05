import os
import csv
import pandas as pd


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
        with open(file_name, newline='', encoding='windows-1257') as csvfile:
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


class Translator:

    data_term_duplicate_options = {1: "'null' after first occurrence", 2: "Add iterated number as suffix", 3: "Leave duplicates in"}
    data_term_duplicate = 3
    data_term_description_options = {1: "Database commentary", 2: "Data glossary compiler commentary", 3: "Database + compiler commentary"}
    data_term_description = 1
    data_term_prefix = ""
    data_term_suffix = ""
    business_term_prefix = ""
    business_term_suffix = ""
    business_term_relation_output_file = r'C:\Users\Administrator\btr.csv'
    term_output_file = r'C:\Users\Administrator\term.csv'
    column_term_relation_output_file = r'C:\Users\Administrator\obj_term_rel.csv'

    def __init__(self):
        self.business_glossary = r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_arisonastik.csv'
        self.data_glossary = r'C:\Users\Administrator\PycharmProjects\hobby_projects\test_andmekirjeldus.csv'

    def is_ready_for_translation(self):
        file_attributes = [self.business_glossary, self.data_glossary, self.term_output_file, self.column_term_relation_output_file, self.business_term_relation_output_file]

        if ("none" in file_attributes) | ("" in file_attributes):
            print('One or more file name attribute missing, set them in the setting menu')
            return False
        if len(set(file_attributes)) != 5:
            print('Duplicate names detected in file names, please change them in settings menu')
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
            self.business_term_relation_output_file = destination
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

            selection = input("Enter selected category: ")
            if selection in ["1", "2", "3"]:
                if option_category == "duplication":
                    self.data_term_duplicate = int(selection)
                if option_category == "description":
                    self.data_term_description = int(selection)
                print("Selection completed!")
                return
            else:
                print("Illegal selection, try again!")

    def translate(self):
        if not self.is_ready_for_translation():
            print('Translation aborted')
            return

        df_bg = pd.read_csv(self.business_glossary, delimiter=';', encoding='windows-1257')
        df_dg = pd.read_csv(self.data_glossary, delimiter=';', encoding='windows-1257')

        print(df_bg.head(5))
        print(df_dg.head(5))



