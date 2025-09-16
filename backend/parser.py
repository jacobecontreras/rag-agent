import os
import csv
csv.field_size_limit(1000000)
from typing import List, Dict, Any


def parse_tsv(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"TSV file not found {file_path}")
    
    data = []

    with open(file_path, 'r', encoding='utf-8') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            data.append(dict(row))
    
    return data


def parse_directory(directory_path: str) -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"LEAPP Directory not found {directory_path}")
    
    results = {}

    for file_name in os.listdir(directory_path):
        if file_name.endswith('.tsv'):
            file_path = os.path.join(directory_path, file_name)
            results[file_name] = parse_tsv(file_path)

    return results