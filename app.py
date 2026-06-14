import json
import os
import unicodedata

DB_FILE = "customSaved.json"

def _sanitize_id(text):
    """
    Converts text to lowercase, replaces spaces with underscores, 
    and strips accents/special characters (e.g., 'Ancião' -> 'anciao').
    """
    if not text:
        return ""
    text = unicodedata.normalize('NFD', str(text))
    text = "".join([c for c in text if not unicodedata.combining(c)])
    return text.lower().strip().replace(" ", "_")

def parse_and_save_json(json_string):
    """Parses the JSON string, extracts only useful information, saves/updates it in the local database."""
    try:
        new_data = json.loads(json_string)
        char_id = _sanitize_id(new_data.get("id"))
        char_name = new_data.get("name")
        char_team = new_data.get("team")
        char_ability = new_data.get("ability")
        
        if not char_id or not char_team or not char_ability or not char_name:
            print("Error: JSON is missing 'id', 'name', 'ability' or 'team'.")
            return None

        # Filter out only the useful information to be saved
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
            print(f"-> Updated existing character '{char_id}' in {DB_FILE}")
        else:
            db.append(filtered_data)
            print(f"-> Added new character '{char_id}' to {DB_FILE}")

        with open(DB_FILE, "w", encoding="utf-8") as file:
            json.dump(db, file, indent=2, ensure_ascii=False)

        return db
    except json.JSONDecodeError:
        print("Error: Invalid JSON string provided.")
        return None

def load_database():
    """Loads and returns the current database list."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def bulk_process_characters(db_list):
    """Processes all characters in the database and writes them cleanly to files."""
    if not db_list:
        print("No characters found in database to process.")
        return

    print(f"\nProcessing {len(db_list)} characters...")

    # 1. Append to reset_in_roles
    for item in db_list:
        modify_reset_in_roles(item["id"])

    # 2. Handle script/set_imported.mcfunction (Insert block starting at Line 206)
    imported_file = os.path.join("script", "set_imported.mcfunction")
    imported_lines = ["\n## CUSTOM\n"]
    
    for item in db_list:
        char_id = item.get("id")
        char_team = item.get("team", "").lower()
        imported_lines.append(
            f"execute if data storage ct:script script_imported{{script:[{char_id}]}} run function ct:script/set_char_data {{char:{char_id},type:{char_team}}}\n"
        )
    _insert_block_at(imported_file, 206, imported_lines)

    # 3. Handle End-Of-File simple append files
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

    # 4. Handle data/character_data.mcfunction (Injected right after "characters": {)
    character_data_file = os.path.join("data", "character_data.mcfunction")
    _inject_into_nbt_file_start(character_data_file, db_list)

    # 5. Handle Client Asset Directory Pack Generation
    _generate_client_assets(db_list)

def modify_reset_in_roles(char_id):
    """Appends the scoreboard command to util/reset_in_roles.mcfunction."""
    file_path = os.path.join("util", "reset_in_roles.mcfunction")
    new_line = f"\nscoreboard players set {char_id} role_list 0"
    try:
        os.makedirs("util", exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(new_line)
        print(f"✓ Updated reset_in_roles for: {char_id}")
    except Exception as e:
        print(f"✗ Failed to update {file_path}: {e}")

def _insert_block_at(file_path, target_line, new_lines):
    """Inserts a list of lines starting at a target line index (1-indexed)."""
    try:
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
        print(f"✓ Inserted custom block into {file_path} starting at line {target_line}")
    except Exception as e:
        print(f"✗ Failed to write to {file_path}: {e}")

def _append_lines_to_file(file_path, new_lines):
    """Directly appends lines to the end of a file without safety searching."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as file:
            file.writelines(new_lines)
        print(f"✓ Appended custom block to the end of {file_path}")
    except Exception as e:
        print(f"✗ Failed to append to {file_path}: {e}")

def _format_nbt_string(text):
    """Encodes strings to preserve internal double quotes and unicode tokens safely inside NBT."""
    if not text:
        return ""
    escaped_quotes = str(text).replace('"', '\\"')
    return escaped_quotes.encode('unicode-escape').decode('utf-8').replace('\\\\u', '\\u')

def _format_reminder_text(text):
    """Converts reminder text to lower case and replaces spaces with underlines."""
    text = _sanitize_id(text)
    if not text:
        return ""
    return str(text).lower().replace(" ", "_")

def _inject_into_nbt_file_start(file_path, db_list):
    """Injects character configurations directly inside NBT scope right after '\"characters\": {'."""
    try:
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
            print(f"✗ Error: Could not find '\"characters\": {{\\' structure inside {file_path}")
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
                reminder_strings = [f"{{text:{_format_reminder_text(rem)},icon:{char_id}}}" for rem in reminders]
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
            
        print(f"✓ Successfully injected characters at the top of NBT scope for {file_path}")
    except Exception as e:
        print(f"✗ Failed to modify NBT file structure {file_path}: {e}")

def _generate_client_assets(db_list):
    """Generates the client side asset directory tree with meta structures and language files."""
    base_dir = "Blood on the Moddedtower"
    lang_dir = os.path.join(base_dir, "assets", "minecraft", "lang")
    
    try:
        os.makedirs(lang_dir, exist_ok=True)
        
        mcmeta_data = {
            "pack": {
                "pack_format": 65,
                "description": "Custom assets for\nBotC modded.",
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
            
        print(f"✓ Successfully built client-side Resource Pack at: '{base_dir}'")
    except Exception as e:
        print(f"✗ Failed to compile client assets package: {e}")