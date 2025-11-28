import ctypes
import os
import json
from pathlib import Path
import logging as lg 
from dotenv import load_dotenv
from core.hashing import get_function_hashes
from core.relations import extract_call_relations
from core.syntaxvalidation import is_syntax_valid
import sys

load_dotenv()

lg.basicConfig(level=lg.INFO, format="%(levelname)s: %(message)s")

FUNCTION_HASH_FILE_NAME = os.getenv("FUNCTION_HASH_FILE_NAME")
FUNCTION_CALLING_RECORD = os.getenv("FUNCTION_CALLING_RECORD")

global_call_relations = {}

print(f"FUNCTION_HASH_FILE_NAME = {FUNCTION_HASH_FILE_NAME}")
print(f"FUNCTION_CALLING_RECORD = {FUNCTION_CALLING_RECORD}")

functions_that_are_changed = []
notify_about_function_behaviour = []

def unique(seq):
    """Return list with duplicates removed while preserving order."""
    return list(dict.fromkeys(seq))

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    input_paths = sys.argv[1:]
    if not input_paths:
        print("No input files provided.")
        exit(0)

    file_paths = []

    for p in input_paths:
        full_path = os.path.join(BASE_DIR, p)

        if os.path.isfile(full_path) and full_path.endswith(".py"):
            file_paths.append(full_path)

        elif os.path.isdir(full_path):
            for root, dirs, files in os.walk(full_path):
                for f in files:
                    if f.endswith(".py"):
                        file_paths.append(os.path.join(root, f))
        else:
            print(f"Skipping invalid path: {p}")    

    for file_path in file_paths:
        print(f"99 - file path = {file_path}")
        if not is_syntax_valid(file_path):
            print("SYNTAX_INVALID")
            exit(0)
        result = get_function_hashes(file_path)
        if not os.path.exists(FUNCTION_HASH_FILE_NAME):
            output_path_for_hash = Path(FUNCTION_HASH_FILE_NAME)
            output_path_for_hash.parent.mkdir(parents=True, exist_ok=True) 
            ctypes.windll.kernel32.SetFileAttributesW(str(output_path_for_hash.parent), 0x02)
            output_path_for_hash.write_text(json.dumps(result, indent=4))
            print(f"✅ Hashes saved to {output_path_for_hash.resolve()}")

        
        else:
            extr_result = json.loads(Path(FUNCTION_HASH_FILE_NAME).read_text())
            for key,val in result.items():
                if key in extr_result:
                    # lg.info("pre-made function hash is being found")
                    if val != extr_result[key]:
                        # lg.info("function is being changed, hence updating")
                        functions_that_are_changed.append(key)
                        extr_result[key] = val
                    else:
                        pass
                else:
                    extr_result[key] = val

            # - writing file 
            Path(FUNCTION_HASH_FILE_NAME).write_text(json.dumps(extr_result, indent=4))

        # extract relations for this file and MERGE into global_call_relations
        call_relations = extract_call_relations(file_path)

        # merge while preserving caller order and avoiding duplicates
        for called_fn, callers in call_relations.items():
            existing_callers = global_call_relations.get(called_fn, [])
            merged = existing_callers + [c for c in callers if c not in existing_callers]
            # append callers preserving order, avoid duplicates
            for c in callers:
                if c not in existing_callers:
                    existing_callers.append(c)
            global_call_relations[called_fn] = merged
    
    # dedupe changed-functions while preserving order
    functions_that_are_changed = unique(functions_that_are_changed)

    already_checked_function = set()

    if len(functions_that_are_changed) > 0:
        for function in functions_that_are_changed:
            callers = global_call_relations.get(function, [])
            for item in callers:   # item = {"caller": "...", "file": "..."}
                notify_about_function_behaviour.append({
                    "function": item["caller"],
                    "file": item["file"]
                })
                
    # remove duplicates by converting each dict to a tuple key
    seen = set()
    unique_list = []

    for item in notify_about_function_behaviour:
        key = (item["file"], item["function"])
        if key not in seen:
            seen.add(key)
            unique_list.append(item)

    notify_about_function_behaviour = unique_list

    print(f"already_checked_function = {already_checked_function}")
    print(f"notify_about_function_behaviour = {notify_about_function_behaviour}")
           
    print(json.dumps(result, indent=4))

print(f"functions_that_are_changed = {functions_that_are_changed}")

print(f"notify_about_function_behaviour = {notify_about_function_behaviour}")

if notify_about_function_behaviour:
    print(f"NOTIFY_FUNCTIONS: {json.dumps(notify_about_function_behaviour)}")