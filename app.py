import json
import os
import shutil
import unicodedata
import __main__ as main

DB_FILE = "customSaved.json"

def _sanitize_id(text):
    # Converts text to lowercase, replaces space with underscore and "unpecialize" characters (e.g., 'Mago Ancião' -> 'mago_anciao')
    if not text:
        return ""
    text = unicodedata.normalize('NFD', str(text))
    text = "".join([c for c in text if not unicodedata.combining(c)])
    return text.lower().strip().replace(" ", "_")

def parse_and_save_json(json_string):
    # Parses the JSON string and saves or updates it in CustomSaved.json
    try:
        new_data = json.loads(json_string)
        char_id = _sanitize_id(new_data.get("id"))
        char_name = new_data.get("name")
        char_team = new_data.get("team")
        char_ability = new_data.get("ability")
        
        if not char_id or not char_team or not char_ability or not char_name:
            
            main.outputy_message("Error: JSON is missing 'id', 'name', 'ability' or 'team'.", "error")
            return None

        # Get only useful information
        filtered_data = {
            "id": char_id,
            "name": char_name,
            "team": char_team,
            "ability": char_ability,
            "firstNightReminder": new_data.get("firstNightReminder"),
            "otherNightReminder": new_data.get("otherNightReminder"),
            "reminders": new_data.get("reminders", []),
            "jinxes": new_data.get("jinxes", [])
        }

        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as file:
                try:
                    db = json.load(file)
                    if not isinstance(db, list):
                        db = []
                except json.JSONDecodeError:
                    db = []
        else:
            db = []

        existing_index = next((i for i, item in enumerate(db) if item["id"] == char_id), None)
        if existing_index is not None:
            db[existing_index] = filtered_data
            main.outputy_message(f"Updated existing character '{char_id}' in {DB_FILE}")
        else:
            db.append(filtered_data)
            main.outputy_message(f"Added new character '{char_id}' to {DB_FILE}", "yey")

        with open(DB_FILE, "w", encoding="utf-8") as file:
            json.dump(db, file, indent=2, ensure_ascii=False)

        return db
    except json.JSONDecodeError:
        main.outputy_message("Error: Invalid JSON string provided.", "error")
        return None

def load_database():
    # Loads and returns the database
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def remove_character(char_id):
    # Removes character
    char_id = _sanitize_id(char_id)
    db = load_database()
    if not db:
        main.outputy_message("Database is empty.")
        return False
    
    new_db = [item for item in db if item["id"] != char_id]
    
    if len(new_db) == len(db):
        main.outputy_message(f"Character '{char_id}' not found in database.")
        return False
    
    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(new_db, file, indent=2, ensure_ascii=False)
    
    main.outputy_message(f"Removed character '{char_id}' from {DB_FILE}", "killer")
    return True

def bulk_process_characters(db_list):
    # Processes all characters in the database and writes them to the files
    if not db_list:
        main.outputy_message("No characters found in the database to process :(", "error")
        return

    print(f"\nAdding {len(db_list)} characters...")

    # 1. Append to reset_in_roles
    for item in db_list:
        modify_reset_in_roles(item["id"])
    print(f"Successfully put characters in {os.path.join('util', 'reset_in_roles.mcfunction')}")

    # 2. Handle script/set_imported.mcfunction (Insert block starting at Line 206)
    imported_file = os.path.join("script", "set_imported.mcfunction")
    imported_lines = ["\n## CUSTOM\n"]
    
    # Map team types for set_char_data
    team_type_map = {
        "townsfolk": "townsfolk",
        "outsider": "outsiders",
        "minion": "minions",
        "demon": "demons",
        "traveller": "travelers"
    }
    
    for item in db_list:
        char_id = item.get("id")
        char_team = item.get("team", "").lower()
        char_type = team_type_map.get(char_team, char_team)  # Use mapped type or fallback to char_team
        imported_lines.append(
            f"execute if data storage ct:script script_imported{{script:[{char_id}]}} run function ct:script/set_char_data {{char:{char_id},type:{char_type}}}\n"
        )
    _insert_block_at(imported_file, 206, imported_lines)

    # 3. separete vanilla characters of custom characters with a 600-inf CUSTOM (I don't know if this can actually go infinite)
    menu_file = os.path.join("admin", "setup", "set_from_menu.mcfunction")
    grim_file = os.path.join("start_game", "roles", "set_grim_roles.mcfunction")
    announce_file = os.path.join("start_game", "roles", "announce.mcfunction")
    
    menu_lines = ["\n## 600-inf CUSTOM\n"]
    grim_lines = ["\n## 600-inf CUSTOM\n"]
    announce_lines = ["\n## 600-inf CUSTOM\n"]

    team_colors = {
        "townsfolk": "#1464e7",
        "outsider": "#1464e7",
        "minion": "#ff4949",
        "demon": "#cf0606"
    }

    for index, item in enumerate(db_list):
        char_id = item.get("id")
        char_team = item.get("team", "").lower()
        numeric_id = 600 + index
        color = team_colors.get(char_team, "#1464e7")

        menu_lines.append(f"execute if score {char_id} role_list matches 1 run data modify storage ct:roles roles insert 0 value {{id:{numeric_id},name:{char_id}}}\n")
        grim_lines.append(f"$execute if entity @s[scores={{role={numeric_id}}}] as @a[tag=storyteller] run fmvariable set p$(id)_role false {char_id}\n")
        announce_lines.append(f'execute as @s[scores={{role={numeric_id}}}] run title @s title [{{"translate":"clocktower.prefix.the","color":"{color}"}},{{"translate":"clocktower.role.{char_id}.name","color":"{color}"}}]\n')
        announce_lines.append(f'execute as @s[scores={{role={numeric_id}}}] run fmvariable set role false {char_id}\n')

    _append_lines_to_file(menu_file, menu_lines)
    _append_lines_to_file(grim_file, grim_lines)
    _append_lines_to_file(announce_file, announce_lines)

    # 4. Handle data/character_data.mcfunction (Kinda scuffed, just injects the data right after "characters": {\)
    character_data_file = os.path.join("data", "character_data.mcfunction")
    _inject_into_nbt_file_start(character_data_file, db_list)

    # 5. Does the resourcepack for the clients
    _generate_client_assets(db_list)

def _backup_path_for(file_path):
    normalized_path = os.path.normpath(file_path)
    if os.path.isabs(normalized_path):
        normalized_path = os.path.relpath(normalized_path, os.getcwd())
    return os.path.join("original_files", normalized_path)


def reset_to_original():
    # Restores files from the dedicated backup folder and deletes resourcepack for clients
    files_to_restore = [
        os.path.join("util", "reset_in_roles.mcfunction"),
        os.path.join("script", "set_imported.mcfunction"),
        os.path.join("admin", "setup", "set_from_menu.mcfunction"),
        os.path.join("start_game", "roles", "set_grim_roles.mcfunction"),
        os.path.join("start_game", "roles", "announce.mcfunction"),
        os.path.join("data", "character_data.mcfunction")
    ]

    for file_path in files_to_restore:
        backup_path = _backup_path_for(file_path)
        if os.path.exists(backup_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            shutil.copy2(backup_path, file_path)
            print(f"Restored: {file_path} from {backup_path}")
    
    asset_dir = "Blood on the Moddedtower"
    if os.path.exists(asset_dir):
        shutil.rmtree(asset_dir)
        print(f"Removed asset directory: {asset_dir}")
    main.outputy_message("files reset to their original state successfully.")

def _ensure_backup(file_path):
    # Creates a backup copy in original_files/<relative-path> if it doesn't already exist
    backup_path = _backup_path_for(file_path)
    if os.path.exists(file_path) and not os.path.exists(backup_path):
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(file_path, backup_path)
        print(f"Created backup for: {file_path} at {backup_path}")

def modify_reset_in_roles(char_id):
    # Appends the scoreboard command to util/reset_in_roles.mcfunction
    file_path = os.path.join("util", "reset_in_roles.mcfunction")
    _ensure_backup(file_path)
    new_line = f"\nscoreboard players set {char_id} role_list 0"
    try:
        os.makedirs("util", exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(new_line)
    except Exception as e:
        main.outputy_message(f"Failed to put characters in {file_path}: {e}", "error")

def _insert_block_at(file_path, target_line, new_lines):
    # Inserts a list of lines starting at a target line
    try:
        _ensure_backup(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n" * target_line)
        
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            
        while len(lines) < target_line:
            lines.append("\n")
            
        for i, line in enumerate(new_lines):
            lines.insert((target_line - 1) + i, line)
        
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)
        print(f"Successfully put characters in {file_path}")
    except Exception as e:
        print(f"Failed to put characters in {file_path}: {e}")

def _append_lines_to_file(file_path, new_lines):
    # Directly appends lines to the end of a file
    try:
        _ensure_backup(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as file:
            file.writelines(new_lines)
        print(f"Successfully put characters in {file_path}")
    except Exception as e:
        print(f"Failed to put characters in {file_path}: {e}")

def _format_nbt_string(text):
    # Encodes strings to preserve internal double quotes and unicode tokens safely inside NBT
    if not text:
        return ""
    escaped_quotes = str(text).replace('"', '\\"')
    return escaped_quotes.encode('unicode-escape').decode('utf-8').replace('\\\\u', '\\u')

def _format_reminder_text(text):
    # Converts reminder text to lower case and replaces spaces with underlines, probably useless now that I made _sanitizer_id but who knows (I should know)
    text = _sanitize_id(text)
    if not text:
        return ""
    return str(text).lower().replace(" ", "_")

def _inject_into_nbt_file_start(file_path, db_list):
    # Injects character configurations directly inside NBT scope right after '\"characters\": {'.
    try:
        _ensure_backup(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as file:
                file.write('data merge storage ct:character_data \\\n{\\\n\t"characters": {\\\n\t}\\\n}')

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        target_index = -1
        for i, line in enumerate(lines):
            cleaned = line.strip().replace(" ", "").replace("\t", "")
            if '"characters":{\\' in cleaned or '"characters":{' in cleaned:
                target_index = i + 1
                break

        if target_index == -1:
            print(f"Failed to put characters in {file_path}: Could not find '\"characters\": {{' structure")
            return

        injected_lines = []
        for item in db_list:
            char_id = item.get("id")
            
            nbt_fields = []
            if item.get("ability"):
                nbt_fields.append(f'"ability": "{_format_nbt_string(item["ability"])}"')
            if item.get("firstNightReminder"):
                nbt_fields.append(f'"first": "{_format_nbt_string(item["firstNightReminder"])}"')
            if item.get("flavor"):
                nbt_fields.append(f'"flavor": "{_format_nbt_string(item["flavor"])}"')
            if item.get("name"):
                nbt_fields.append(f'"name": "{_format_nbt_string(item["name"])}"')
            if item.get("otherNightReminder"):
                nbt_fields.append(f'"other": "{_format_nbt_string(item["otherNightReminder"])}"')
                
            reminders = item.get("reminders", [])
            if reminders:
                reminder_strings = [f"{{text:{char_id}_{_format_reminder_text(rem)},icon:{char_id}}}" for rem in reminders]
                nbt_fields.append(f'"reminders": [{",".join(reminder_strings)}]')
                
            jinxes = item.get("jinxes", [])
            if jinxes:
                jinx_strings = [f"{{id:{j.get('id')}}}" for j in jinxes if isinstance(j, dict) and j.get("id")]
                if jinx_strings:
                    nbt_fields.append(f'"jinxes": [{",".join(jinx_strings)}]')

            joined_fields = ",\\\n\t\t\t".join(nbt_fields)
            
            char_block = (
                f'\t\t"{char_id}": {{\\\n'
                f'\t\t\t{joined_fields}\\\n'
                f'\t\t}},\\\n'
            )
            injected_lines.append(char_block)

        for line in reversed(injected_lines):
            lines.insert(target_index, line)

        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)
            
        print(f"Successfully put characters in {file_path}")
    except Exception as e:
        print(f"Failed to put characters in {file_path}: {e}")

def _generate_client_assets(db_list):
    # Generates the client side resourcepack
    base_dir = "Blood on the Moddedtower"
    lang_dir = os.path.join(base_dir, "assets", "minecraft", "lang")
    
    try:
        os.makedirs(lang_dir, exist_ok=True)
        
        mcmeta_data = {
            "pack": {
                "pack_format": 65,
                "description": "Custom assets for\nBotC custom characters.",
                "max_format": 1000,
                "min_format": 65
            }
        }
        with open(os.path.join(base_dir, "pack.mcmeta"), "w", encoding="utf-8") as file:
            json.dump(mcmeta_data, file, indent=4, ensure_ascii=False)
            
        lang_data = {}
        for item in db_list:
            char_id = item.get("id")
            char_name = item.get("name", char_id) # Falls back to id if name field is missing
            
            # Now mapping translation to the 'name' property instead of 'id'
            lang_data[f"clocktower.role.{char_id}.name"] = str(char_name)
            lang_data[f"clocktower.role.{char_id}.desc"] = item.get("ability", "")
            
            reminders = item.get("reminders", [])
            for rem in reminders:
                formatted_rem_key = _format_reminder_text(rem)
                lang_data[f"clocktower.reminder.{char_id}_{formatted_rem_key}.text"] = str(rem)
                
        with open(os.path.join(lang_dir, "en_us.json"), "w", encoding="utf-8") as file:
            json.dump(lang_data, file, indent=4, ensure_ascii=False)
            
        main.outputy_message(f"Successfully made the client resourcepack {base_dir}", "yey")
    except Exception as e:
        main.outputy_message(f"Failed to make the client resourcepack {base_dir}: {e}", "error")