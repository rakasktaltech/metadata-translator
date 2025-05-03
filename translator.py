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
        with open(file_name, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            # Try reading at least one row to validate structure
            first_row = next(reader, None)
            if first_row is None or len(first_row) < 1:
                return False
    except (OSError, UnicodeDecodeError, csv.Error):
        print("Could not verify the files contents as suitable! Try another file!")
        return False

    return True


class Translator:
    def __init__(self):
        self.business_glossary = "none"
        self.data_glossary = "none"
        self.parameters = "default.txt"

    def set_file(self, file_type):
        destination = input(f"Insert {file_type} glossary .csv files' absolute address:")
        if not is_correct_file(destination):
            pass
        elif file_type == "business":
            self.business_glossary = destination
        elif file_type == "data":
            self.data_glossary = destination
