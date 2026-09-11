import app
import json
import tkinter as tk
from tkinter import filedialog

#WINDOW MAGIC
root = tk.Tk()
root.geometry("900x500")
root.minsize(600, 300)
root.title("MAAT's Buddy's Sybillian's Minecraft Blood on the Clocktower Custom character Installer")

#   COMMANDS

def outputy_message(message: str, emote: str = "happy"):
    if emote == "yey":
        outputy_msg.config(text=f"[^ ω ^] - {message}")
    elif emote == "killer":
        outputy_msg.config(text=f"[ಠ ω ಠ] - {message}")
    elif emote == "error":
        outputy_msg.config(text=f"[X o X] - {message}")
    elif emote == "fish":
        outputy_msg.config(text=f"( ͡° ͜ʖ ͡°) - {message}")
    else:
        outputy_msg.config(text=f"[O u O] - {message}")

def add_to_list():
    user_input = entry.get("1.0", tk.END).strip()
    outputy_message("You gotta put something in first silly!", "happy")
    if user_input:
        app.parse_and_save_json(user_input)
        entry.delete("1.0", tk.END)
    update_char_list()

def import_json():
    file_path = filedialog.askopenfilename(title="Select your JSON file with all your custom characters (it can be a script with vanilla characters) ", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                json_data = json.load(file)
                for item in json_data:
                    item_dumped = json.dumps(item)
                    app.parse_and_save_json(item_dumped)
                update_char_list()
                outputy_message("Imported/Updated as many characters as possible.", "yey")
            except json.JSONDecodeError:
                outputy_message("Error: Invalid JSON file.", "error")
    else:
        outputy_message("Error: No file selected.", "error")

def insert_characters():
    db_list = app.load_database()
    if db_list:
        app.bulk_process_characters(db_list)
        outputy_message("All characters successfully installed into .mcfunction files!", "yey")
    else:
        outputy_message("Database is empty! Paste some character JSONs first.", "error")

def remove_character():
    char_id = entry.get("1.0", tk.END).strip()
    if char_id:
        app.remove_character(char_id)
        entry.delete("1.0", tk.END)
        update_char_list()
    else:
        outputy_message("Please provide a character ID to remove. Or a json string if an id", "error")

def reset_to_original():
    app.reset_to_original()

def update_char_list():
    app.check_if_db_exists()
    with open("CustomSaved.json", "r") as f:
        db_list = json.load(f)

    text_list.delete(0, tk.END)
    for char in db_list:
        text_list.insert(tk.END, f"{char['name']}")

def show_character():
    selected_index = text_list.curselection()
    if selected_index:
        char_name = text_list.get(selected_index)
        with open("CustomSaved.json", "r", encoding="utf-8") as f:
            db_list = json.load(f)
        
        target_char = next((item for item in db_list if item.get("name") == char_name), None)

        entry.delete(1.0, tk.END)
        entry.insert(tk.END, json.dumps(target_char, indent=2, ensure_ascii=False))
        print(f"Showing info for {char_name}: {json.dumps(target_char, indent=2, ensure_ascii=False)}")

        outputy_message(f"Showing info for {char_name}", "yey")

#   FRAMES

output_frame = tk.Frame(root, bg="chartreuse4")
output_frame.grid(row=0, column=0, sticky="news")
root.columnconfigure(0, weight=1)

input_frame = tk.Frame(root, bg="light gray")
input_frame.grid(row=1, column=0, rowspan=5, sticky="news")
root.columnconfigure(0, weight=1)

for row_num in range(root.grid_size()[1]):
    root.rowconfigure(row_num, weight=1)

root.rowconfigure(1, weight=6)

#   INPUT

entry = tk.Text(input_frame, font=("Arial", 12), wrap="word", height=4, width=20)
entry.grid(row=0, column=0, rowspan=4, columnspan=2, sticky="nsew", padx=5, pady=20)

add_btn = tk.Button(input_frame, text="-------------------->\nadd character to list", command=add_to_list, relief="raised")
add_btn.grid(row=0, column=2, sticky="nsew", padx=2, pady=10)

insert_btn = tk.Button(input_frame, text="Put all saved character in the file\n(remember to reset before adding new characters)", command=insert_characters, relief="raised")
insert_btn.grid(row=1, column=2, sticky="nsew", padx=2, pady=5)

remove_btn = tk.Button(input_frame, text="remove character\n(put id in textbox or double click name on the right)", command=remove_character, relief="raised")
remove_btn.grid(row=2, column=2, sticky="nsew", padx=2, pady=5)

reset_btn = tk.Button(input_frame, text="reset to original", command=reset_to_original, relief="raised")
reset_btn.grid(row=3, column=2, sticky="nsew", padx=2, pady=10)

text_list = tk.Listbox(input_frame)
text_list.grid(row=0, column=3, rowspan=4, sticky="nsew", padx=5, pady=10)
text_list.bind("<Double-Button-1>", lambda event: show_character())

fish_btn = tk.Button(input_frame, text="Fish", command=lambda: outputy_message("And you know what that means!", "fish"))
fish_btn.grid(row=3, column=4)

import_btn = tk.Button(input_frame, text="Import .json", command=import_json)
import_btn.grid(row=2, column=4)

for row_num in range(input_frame.grid_size()[1]):
    input_frame.rowconfigure(row_num, weight=1)
for col_num in range(input_frame.grid_size()[0]):
    input_frame.columnconfigure(col_num, weight=1)

input_frame.columnconfigure(0, weight=3)
input_frame.columnconfigure(2, weight=3)

#   OUTPUTY

outputy_msg = tk.Label(output_frame, text="[O u O] - Hi! I'm Outputy! The text area that gives feedback on any input", font=("Arial", 12), bg="chartreuse2", wraplength=700)
outputy_msg.grid(row=0, column=0, sticky="w")
output_frame.rowconfigure(0, weight=1)

update_char_list()
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