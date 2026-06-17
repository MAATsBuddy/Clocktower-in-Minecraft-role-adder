import app

def main():
    print("=== Blood on the Clocktower Custom Installer ===")
    print("-> Paste character JSONs to save them to the database.")
    print("-> Type 'insert' to generate commands for all saved characters.")
    print("-> Type 'reset' to restore files to their original state.")
    print("-> Leave the input completely blank and press Enter to exit.\n")
    
    while True:
        print("-" * 50)
        print("Paste JSON (Press Enter -> Ctrl+Z -> Enter again to submit)")
        print("OR type 'insert' to generate commands / press Enter on a blank line to exit:")
        
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
                
        user_input = "".join(lines).strip()
        
        # Scenario 1: Exit
        if not user_input:
            print("\nExiting program. Goodbye!")
            break

        # Scenario: Reset files to original state
        if user_input.lower() == "reset":
            app.reset_to_original()
            print("\nReset process finished.")
            continue
            
        # Scenario 2: Generate/Insert All Bulk Process
        if user_input.lower() == "insert":
            db_list = app.load_database()
            if db_list:
                app.bulk_process_characters(db_list)
                print("\nAll characters successfully installed into .mcfunction files!")
            else:
                print("\nDatabase is empty! Paste some character JSONs first.")
            continue
            
        # Scenario 3: Save incoming JSON data
        app.parse_and_save_json(user_input)

if __name__ == "__main__":
    main()