import os
from parsers.tsv_parser import parse_tsv_directory
from parsers.leapp_db_parser import parse_spatial_db, parse_timeline_db
from database.database import update_report_status, store_tsv_data, store_spatial_data, store_timeline_data
from utils.embedding_utils import embed_job_data

# Ensures the chosen directory contains the correct directory names
def validate_leapp_directory(directory_path: str) -> bool:
    """Validate LEAPP directory structure"""
    required_dirs = ['_TSV Exports', '_KML Exports', '_Timeline']

    if not os.path.exists(directory_path):
        return False

    for dir_name in required_dirs:
        if not os.path.exists(os.path.join(directory_path, dir_name)):
            return False

    return True

# Parse and store data from directories
def process_leapp_report(job_name: str, directory_path: str):
    """Main processing pipeline"""
    try:
        update_report_status(job_name, "processing")

        # Parse TSV files
        tsv_data = parse_tsv_directory(os.path.join(directory_path, '_TSV Exports'))
        store_tsv_data(job_name, tsv_data)

        # Parse spatial data
        spatial_path = os.path.join(directory_path, '_KML Exports', '_latlong.db')
        if os.path.exists(spatial_path):
            spatial_data = parse_spatial_db(spatial_path)
            store_spatial_data(job_name, spatial_data)

        # Parse timeline data
        timeline_path = os.path.join(directory_path, '_Timeline', 'tl.db')
        if os.path.exists(timeline_path):
            timeline_data = parse_timeline_db(timeline_path)
            store_timeline_data(job_name, timeline_data)

        update_report_status(job_name, "completed")

        # Start embedding process
        embed_job_data(job_name)

    except Exception as e:
        update_report_status(job_name, "failed", str(e))