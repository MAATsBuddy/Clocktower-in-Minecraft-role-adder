import app
import json
import tkinter as tk
from tkinter import filedialog
import multiprocessing

#WINDOW MAGIC
root = tk.Tk()
root.geometry("900x500")
root.minsize(600, 300)
root.title("MAAT's Buddy's Sybillian's Clocktower in Minecraft Custom character Installer")

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
                outputy_message("Imported/Updated all characters found.", "yey")
            except json.JSONDecodeError:
                outputy_message("Error: Invalid JSON file.", "error")
    else:
        outputy_message("Error: No file selected.", "error")

def insert_characters():
    app.reset_to_original()
    db_list = app.load_database()
    outputy_message("All characters successfully installed into .mcfunction files!", "yey")
    app.bulk_process_characters(db_list)    

def remove_character():
    char_id = entry.get("1.0", tk.END).strip()
    if char_id:
        app.remove_character(char_id)
        entry.delete("1.0", tk.END)
        update_char_list()
    else:
        outputy_message("Please provide a character ID to remove. Or a json string if an id", "error")

def clear_all():
    db_list = app.load_database()
    for char in db_list:
        app.remove_character(char.get("id"))
    update_char_list()
    outputy_message("All characters have been BRUTALLY DESTROYED!", "yey")

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

def make_bag_text():
    file_path = filedialog.askopenfilename(title="Select your JSON file with all your custom characters (it can be a script with vanilla characters) ", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                json_data = json.load(file)
                bag_txt.delete("1.0", tk.END)

                bag_txt.insert(tk.END, "[{\"id\":\"_meta\",\"author\":\"")
                bag_txt.insert(tk.END, json_data[0]['author'])
                bag_txt.insert(tk.END, "\",\"name\":\"")
                bag_txt.insert(tk.END, json_data[0]['name'])
                bag_txt.insert(tk.END, "\"}")

                for item in json_data[1:]:
                    if 'id' not in item:
                        bag_txt.insert(tk.END, ",\"")
                        bag_txt.insert(tk.END, item)
                        bag_txt.insert(tk.END, "\"")
                        continue
                    bag_txt.insert(tk.END, ",")
                    bag_txt.insert(tk.END, json.dumps(item['id'], ensure_ascii=False))

                bag_txt.insert(tk.END, "]")
                outputy_message("Formed your bag! Now just copy this and paste in the text box in \"change script\"", "yey")
            except json.JSONDecodeError:
                outputy_message("Error: Invalid JSON file.", "error")
    else:
        outputy_message("Error: No file selected.", "error")
#   FRAMES

output_frame = tk.Frame(root, bg="chartreuse4")
output_frame.grid(row=0, column=0, sticky="news")

input_frame = tk.Frame(root, bg="light gray")
input_frame.grid(row=1, column=0, rowspan=5, sticky="news")

under_frame = tk.Frame(root, bg="light gray")
under_frame.grid(row=6, column=0, sticky="news")

root.columnconfigure(0, weight=1)

for row_num in range(root.grid_size()[1]):
    root.rowconfigure(row_num, weight=1)

root.rowconfigure(1, weight=6)

#   INPUT

entry = tk.Text(input_frame, font=("Arial", 12), wrap="word", height=4, width=20)
entry.grid(row=0, column=0, rowspan=4, columnspan=2, sticky="nsew", padx=5, pady=20)

add_btn = tk.Button(input_frame, text="-------------------->\nadd/update character to list", command=add_to_list, relief="raised")
add_btn.grid(row=0, column=2, sticky="nsew", padx=2, pady=10)

insert_btn = tk.Button(input_frame, text="Put all saved character into the game files\n(the file resets automatically before putting new characters)", command=insert_characters, relief="raised")
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

clear_btn = tk.Button(input_frame, text="Clear all", command=clear_all)
clear_btn.grid(row=1, column=4)

for row_num in range(input_frame.grid_size()[1]):
    input_frame.rowconfigure(row_num, weight=1)
for col_num in range(input_frame.grid_size()[0]):
    input_frame.columnconfigure(col_num, weight=1)

under_frame.rowconfigure(0, weight=1)
input_frame.columnconfigure(2, weight=3)

#   OUTPUTY

outputy_msg = tk.Label(output_frame, text="[O u O] - Hi! I'm Outputy! The text area that gives feedback on any input", font=("Arial", 12), bg="chartreuse2", wraplength=700)
outputy_msg.grid(row=0, column=0, sticky="w")
output_frame.rowconfigure(0, weight=1)

#   SCRIPT TEXT

add_btn = tk.Button(under_frame, text="Make Bag Text", command=make_bag_text, relief="raised")
add_btn.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
under_frame.columnconfigure(0, weight=1)

bag_txt = tk.Text(under_frame, font=("Arial", 10), height=5, width=110, wrap="word")
bag_txt.insert(tk.END, "(Press the \"Make Bag Text\" button to make the text for you to put in your bag and load the script)")
bag_txt.grid(row=0, column=1, sticky="wsen", padx=10, pady=10)
under_frame.columnconfigure(1, weight=2)

under_frame.rowconfigure(0, weight=1)

update_char_list()

if __name__ == "__main__":

    multiprocessing.freeze_support()

    root.mainloop()