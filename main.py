import ctypes
import os 
import ast
import hashlib
import json
from pathlib import Path
from typing import Dict
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

    input_files = sys.argv[1:]  # Get input files from command-line arguments
    if not input_files:
        print("No input files provided.")
        exit(0)

    file_paths = [os.path.join(BASE_DIR, f) for f in input_files]
    for file_path in file_paths:
        print(f"99 - file path = {file_path}")
        if not is_syntax_valid(file_path):
            print("SYNTAX_INVALID")
            exit(0)
        result = get_function_hashes(file_path)
        if not os.path.exists(FUNCTION_HASH_FILE_NAME):
            # lg.info("creating the new function hash file")
            output_path_for_hash = Path(FUNCTION_HASH_FILE_NAME)
            output_path_for_hash.parent.mkdir(parents=True, exist_ok=True) 
            ctypes.windll.kernel32.SetFileAttributesW(str(output_path_for_hash.parent), 0x02)
            output_path_for_hash.write_text(json.dumps(result, indent=4))
            print(f"✅ Hashes saved to {output_path_for_hash.resolve()}")
        
        else:
            # - here their is no Logic of reading the currently made file as their will be no back version for comparison
            # - when the hash funciton is already present, then checking if the hash is changed, if yes the do overwrite & if not present then 
            #   do make a entry of it
            # lg.info("reading the pre-made function hash file")
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
                    # lg.info("function hash is not found, hence adding it in function's hash-file")
                    extr_result[key] = val

            # - writing file 
            Path(FUNCTION_HASH_FILE_NAME).write_text(json.dumps(extr_result, indent=4))

        # extract relations for this file and MERGE into global_call_relations
        call_relations = extract_call_relations(file_path)

        # merge while preserving caller order and avoiding duplicates
        for called_fn, callers in call_relations.items():
            existing_callers = global_call_relations.get(called_fn, [])
            # append callers preserving order, avoid duplicates
            for c in callers:
                if c not in existing_callers:
                    existing_callers.append(c)
            global_call_relations[called_fn] = existing_callers
    
    # dedupe changed-functions while preserving order
    functions_that_are_changed = unique(functions_that_are_changed)

    if len(functions_that_are_changed) > 0:
        for function in functions_that_are_changed:
            print(f"function = {function}")
            val_found = global_call_relations.get(function, [])
            if val_found:
                print(f"inside = {val_found}")
                for i in val_found:
                    notify_about_function_behaviour.append(i)
            else:
                pass

    print(json.dumps(result, indent=4))

    # print(json.dumps(call_relations, indent=4))

print(f"functions_that_are_changed = {functions_that_are_changed}")

# dedupe notify list and preserve order
notify_about_function_behaviour = unique(notify_about_function_behaviour)

print(f"notify_about_function_behaviour = {notify_about_function_behaviour}")

if notify_about_function_behaviour:
    print(f"NOTIFY_FUNCTIONS: {json.dumps(notify_about_function_behaviour)}")
