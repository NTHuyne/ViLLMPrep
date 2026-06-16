import re
import json


def load_jsonl(data_path):
    data = []
    with open(data_path, mode='r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def get_items_from_output(text):
    items = [match.strip() for match in re.findall(r'\d+\.\s*(.+)', text)]
    return items


def formating_alpaca_dataset(data, file_dir):
    alpaca_data = []
    for d in data:
        alpaca_data.append({
            "instruction": "",
            "input": d["question"],
            "output": d["answer"]
        })
    with open(file_dir, 'a', encoding='utf-8') as file:
        for sample in alpaca_data:
            json.dump(sample, file, ensure_ascii=False)
            file.write('\n')
