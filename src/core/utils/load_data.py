import json
import os


def load_jsonl(data_path):
    data = []
    with open(data_path, mode='r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def get_relative_jsonl_paths(folder_path):
    # List to store the relative paths of all *.jsonl files
    relative_paths = []

    # Iterate through all files in the directory and subdirectories
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.jsonl'):  # Check if the file is a .jsonl file
                # Get the relative path
                relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                relative_paths.append(relative_path)
    return relative_paths
