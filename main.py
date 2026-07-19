import app
import tkinter as tk

#WINDOW MAGIC
root = tk.Tk()
root.geometry("900x300")
root.title("MAAT's Buddy's Sybillian's Minecraft Blood on the Clocktower Custom character Installer")

#   COMMANDS

def add_to_list():
    user_input = entry.get()
    if user_input:
        app.parse_and_save_json(user_input)
        entry.delete(0, tk.END)

def insert_characters():
    db_list = app.load_database()
    if db_list:
        app.bulk_process_characters(db_list)
        print("\nAll characters successfully installed into .mcfunction files!")
    else:
        print("\nDatabase is empty! Paste some character JSONs first.")

def remove_character():
    char_id = entry.get()
    if char_id:
        app.remove_character(char_id)
        entry.delete(0, tk.END)
    else:
        print("Please provide a character ID to remove. Type ONLY the ID")

def reset_to_original():
    app.reset_to_original()
    print("\nReset process finished.")

#   FRAMES

button_frame = tk.Frame(root)
button_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

output_frame = tk.Frame(root)
output_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

for row_num in range(root.grid_size()[1]):
    root.rowconfigure(row_num, weight=1)
for col_num in range(root.grid_size()[0]):
    root.columnconfigure(col_num, weight=1)

#   STUFF

entry = tk.Entry(button_frame)
entry.grid(row=0, column=0, rowspan=4, sticky="nsew")

entry.bind("<Return>", lambda event: add_to_list())

add_btn = tk.Button(button_frame, text="add character to list", command=add_to_list)
add_btn.grid(row=0, column=1)

insert_btn = tk.Button(button_frame, text="Put all saved character in the file\n(remember to reset before adding new characters)", command=insert_characters)
insert_btn.grid(row=1, column=1)

remove_btn = tk.Button(button_frame, text="remove character\n(put id in textbox)", command=remove_character)
remove_btn.grid(row=2, column=1)

reset_btn = tk.Button(button_frame, text="reset to original", command=reset_to_original)
reset_btn.grid(row=3, column=1)

for row_num in range(button_frame.grid_size()[1]):
    button_frame.rowconfigure(row_num, weight=1)
for col_num in range(button_frame.grid_size()[0]):
    button_frame.columnconfigure(col_num, weight=1)

button_frame.columnconfigure(0, weight=3)

fish_btn = tk.Button(output_frame, text="Fish\nbutton")
fish_btn.grid(row=0, column=1)

text_list = tk.Listbox(output_frame)
text_list.grid(row=0, column=0, sticky="nsew")

for row_num in range(output_frame.grid_size()[1]):
    output_frame.rowconfigure(row_num, weight=1)
for col_num in range(output_frame.grid_size()[0]):
    output_frame.columnconfigure(col_num, weight=1)

output_frame.columnconfigure(0, weight=3)

root.mainloop()

# def main():
#     print("=== Blood on the Clocktower Custom Installer ===")
#     print("-> Paste character JSONs to save them to the database.")
#     print("-> Type 'insert' to generate commands for all saved characters.")
#     print("-> Type 'reset' to restore files to their original state.")
#     print("-> Type 'remove [character id]' to delete a character.")
#     print("-> Leave the input completely blank and press Enter to exit.\n")

#     while True:
#         print("-" * 50)
#         print("Paste JSON (Press Enter -> Ctrl+Z -> Enter again to submit)")
#         print("OR type 'insert' to generate commands / press Enter on a blank line to exit:")
        
#         lines = []
#         while True:
#             try:
#                 line = input()
#                 lines.append(line)
#             except EOFError:
#                 break
#         user_input = "".join(lines).strip()
        
#         # Scenario 1: Exit
#         if not user_input:
#             print("\nExiting program. Goodbye!")
#             break

#         # Scenario 2: Reset files to original state
#         if user_input.lower() == "reset":
#             app.reset_to_original()
#             print("\nReset process finished.")
#             continue
            
#         # Scenario 3: Remove a character
#         if user_input.lower().startswith("remove "):
#             char_id = user_input[7:].strip()
#             if char_id:
#                 app.remove_character(char_id)
#             else:
#                 print("Please provide a character ID to remove. Usage: remove [id]")
#             continue
            
#         # Scenario 4: Generate/Insert All Bulk Process
#         if user_input.lower() == "insert":
#             db_list = app.load_database()
#             if db_list:
#                 app.bulk_process_characters(db_list)
#                 print("\nAll characters successfully installed into .mcfunction files!")
#             else:
#                 print("\nDatabase is empty! Paste some character JSONs first.")
#             continue
            
#         # Scenario 5: Save incoming JSON data
#         app.parse_and_save_json(user_input)

# if __name__ == "__main__":
#     main()