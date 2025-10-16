import os
import csv
import logging
from typing import List, Dict, Any

csv.field_size_limit(10000000)  # 10MB
logger = logging.getLogger(__name__)

def parse_tsv(file_path: str) -> List[Dict[str, Any]]:
    """Parse a TSV file and return list of dictionaries"""
    if not os.path.exists(file_path):
        logger.error(f"TSV file not found: {file_path}")
        raise FileNotFoundError(f"TSV file not found {file_path}")

    logger.debug(f"Parsing TSV file: {file_path}")
    with open(file_path) as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        data = list(reader)
        logger.info(f"Parsed {len(data)} rows from {file_path}")
        return data


def parse_tsv_directory(directory_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Parse all TSV files in a directory and return filename -> data mapping"""
    if not os.path.exists(directory_path):
        logger.error(f"LEAPP directory not found: {directory_path}")
        raise FileNotFoundError(f"LEAPP Directory not found {directory_path}")

    logger.info(f"Parsing TSV directory: {directory_path}")
    results = {}
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.tsv'):
            file_path = os.path.join(directory_path, file_name)
            results[file_name] = parse_tsv(file_path)

    total_rows = sum(len(data) for data in results.values())
    logger.info(f"Parsed {len(results)} TSV files with {total_rows} total rows")
    return results