import os
import csv


def is_correct_file(file_name):
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

    data_term_duplicate_options = {1: "null after first occurrence", 2: "Add iterated number as suffix", 3: "Leave duplicates in"}
    data_term_duplicate = 1
    data_term_description_options = {1: "Database commentary", 2: "Data glossary compiler commentary", 3: "Database + compiler commentary"}
    data_term_description = 1
    data_term_prefix = ""
    data_term_suffix = ""
    business_term_prefix = ""
    business_term_suffix = ""
    business_term_relation_output_file = ""
    term_output_file = ""
    column_term_relation_output_file = ""

    def __init__(self):
        self.business_glossary = "none"
        self.data_glossary = "none"

    def set_input_file(self, file_type):
        destination = input(f"Insert {file_type} glossary .csv files' absolute address:")
        if not is_correct_file(destination):
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

    def set_addon(self, term_type, addon_type):
        pass