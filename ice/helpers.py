import os
import re


def get_latest(dir, search_term):
    files = os.listdir(dir)
    matching_files = [os.path.join(dir, f) for f in files if re.search(search_term, f)]
    if not matching_files:
        return None
    latest_file = max(matching_files, key=os.path.getctime)
    print(latest_file)
    return latest_file
