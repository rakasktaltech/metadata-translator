
import translator

def display_menu(translator_obj):
    print("\n" * 50)
    while True:
        print("#######################")
        print("Data catalog translator")
        print("#######################")
        print(f"Currently selected business glossary: ", translator_obj.business_glossary)
        print(f"Currently selected data glossary: ", translator_obj.data_glossary)
        print("#######################")
        print("Select action from menu:")
        print("1) Set business glossary file")
        print("2) Set data glossary file")
        print("3) View translation settings")
        print("4) Change translation settings")
        print("5) Translate to import files")
        print("6) Exit")
        print("")

        reply = input("Insert selection here:")

        match reply:
            case "1":
                translator_obj.set_file("business")
            case "2":
                translator_obj.set_file("data")
            case "3":
                translator_obj.print_settings()
            case "4":
                print("4 selected")
            case "5":
                print("5 selected")
            case "6":
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