import translator


def display_change_settings(tr_obj):
    print("\n" * 50)
    while True:
        print(f'1) Data term prefix added by translation: {tr_obj.data_term_prefix}')
        print(f'2) Data term suffix added by translation: {tr_obj.data_term_suffix}')
        print(f'3) Business term prefix added by translation: {tr_obj.business_term_prefix}')
        print(f'4) Business term suffix added by translation: {tr_obj.business_term_suffix}')
        print(f'5) Data term duplication option selected: {tr_obj.data_term_duplicate_options.get(tr_obj.data_term_duplicate)}')
        print(f'6) Data term description option selected: {tr_obj.data_term_description_options.get(tr_obj.data_term_description)}')
        print(f'7) Term output file absolute address: {tr_obj.term_output_file}')
        print(f'8) Business term relation output file absolute address: {tr_obj.business_term_relation_output_file}')
        print(f'9) Data object and term relation output file: {tr_obj.column_term_relation_output_file}')
        print(f'0) Return to main menu')
        selection = input("Please select a setting to change or exit settings menu")

        match selection:
            case "0":
                break
            case "1":
                tr_obj.set_addon("data", "prefix")
            case "2":
                tr_obj.set_addon("data", "suffix")
            case "3":
                tr_obj.set_addon("business", "prefix")
            case "4":
                tr_obj.set_addon("business", "suffix")
            case "5":
                pass
            case "6":
                pass
            case "7":
                tr_obj.set_output_file("terms")
            case "8":
                tr_obj.set_output_file("business term relation")
            case "9":
                tr_obj.set_output_file("object term relation")
            case _:
                print("\n" * 50)
                print("Input not in range '0'-'9', please insert valid number")

def display_menu(tr_obj):
    print("\n" * 50)
    while True:
        print("#######################")
        print("Data catalog translator")
        print("#######################")
        print(f"Currently selected business glossary: ", tr_obj.business_glossary)
        print(f"Currently selected data glossary: ", tr_obj.data_glossary)
        print("#######################")
        print("Select action from menu:")
        print("1) Set business glossary file")
        print("2) Set data glossary file")
        print("3) View and change translation settings")
        print("4) Translate to import files")
        print("5) Exit")
        print("")

        reply = input("Insert selection here:")

        match reply:
            case "1":
                tr_obj.set_input_file("business")
            case "2":
                tr_obj.set_input_file("data")
            case "3":
                display_change_settings(tr_obj)
            case "4":
                print("4 selected")
            case "5":
                break
            case _:
                print("\n" * 50)
                print("Illegal input, try again")


def display_exit_message():
    print("\n" * 50)
    print("#######################")
    print("Thank You for using data catalog translator")
    print("#######################")


if __name__ == '__main__':
    trans = translator.Translator()
    display_menu(trans)
    display_exit_message()