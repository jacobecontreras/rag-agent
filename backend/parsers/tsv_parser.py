import os
import csv
from typing import List, Dict, Any
csv.field_size_limit(10000000) # 10MB

# Parse a tsv file row by row
def parse_tsv(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"TSV file not found {file_path}")
    
    data = []

    with open(file_path) as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            data.append(row)
    
    return data

# Finds and parses tsv files
def parse_tsv_directory(directory_path: str) -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"LEAPP Directory not found {directory_path}")
    
    results = {}

    for file_name in os.listdir(directory_path):
        if file_name.endswith('.tsv'):
            file_path = os.path.join(directory_path, file_name)
            results[file_name] = parse_tsv(file_path)

    return results