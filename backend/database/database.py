import os
import json
import sqlite3
import logging
from typing import List, Dict, Any
from contextlib import contextmanager

DB_NAME = "leapp_forensics.db"
DEFAULT_STATUS = "processing"

logger = logging.getLogger(__name__)

def init_database():
    # Create database file in same directory as this script
    conn = get_db_connection()
    cursor = conn.cursor()

    # Main report metadata table: stores info about each uploaded report
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT UNIQUE NOT NULL,         -- Unique identifier for each report job
            report_path TEXT NOT NULL,              -- File system path to the report directory
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'processing',      -- processing/completed/failed
            error_message TEXT                       -- Error details if processing failed
        )
    ''')

    # Information about TSV files found in each report
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artifact_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,                -- Links to reports table
            file_name TEXT NOT NULL,               -- Original TSV filename
            artifact_name TEXT,                    -- Display name (cleaned up filename)
            FOREIGN KEY (job_name) REFERENCES reports(job_name) ON DELETE CASCADE,
            UNIQUE(job_name, file_name)           -- Prevent duplicate files per report
        )
    ''')

    # Actual data rows from TSV files, stored as JSON
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artifact_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,                -- Links to reports table
            artifact_type_id INTEGER NOT NULL,     -- Links to artifact_types table
            row_index INTEGER NOT NULL,            -- Row number from original TSV
            data_json TEXT NOT NULL,                -- Row data serialized as JSON
            FOREIGN KEY (job_name) REFERENCES reports(job_name) ON DELETE CASCADE,
            FOREIGN KEY (artifact_type_id) REFERENCES artifact_types(id) ON DELETE CASCADE
        )
    ''')

    # GPS/location data extracted from KML files
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spatial_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,                -- Links to reports table
            timestamp TEXT,                         -- Time of location event
            latitude TEXT,                          -- GPS latitude coordinate
            longitude TEXT,                         -- GPS longitude coordinate
            activity TEXT,                          -- What was happening at this location
            source_artifact TEXT,                   -- Which file this data came from
            FOREIGN KEY (job_name) REFERENCES reports(job_name) ON DELETE CASCADE
        )
    ''')

    # Timeline events from Timeline directory files
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,                -- Links to reports table
            key TEXT,                               -- Event identifier/unique key
            activity TEXT,                          -- Event description
            datalist TEXT,                          -- Additional event information
            source_artifact TEXT,                   -- Source file for this event
            FOREIGN KEY (job_name) REFERENCES reports(job_name) ON DELETE CASCADE
        )
    ''')

    # Save changes and close connection
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(os.path.join(os.path.dirname(__file__), DB_NAME))

@contextmanager
def get_db_cursor():
    """Context manager for database operations"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_report_metadata(job_name: str, report_path: str):
    """Insert report metadata"""
    with get_db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO reports (job_name, report_path, status) VALUES (?, ?, ?)",
            (job_name, report_path, DEFAULT_STATUS)
        )

def update_report_status(job_name: str, status: str, error_message: str = None):
    """Update report processing status"""
    with get_db_cursor() as cursor:
        if error_message:
            cursor.execute(
                "UPDATE reports SET status = ?, error_message = ? WHERE job_name = ?",
                (status, error_message, job_name)
            )
        else:
            cursor.execute(
                "UPDATE reports SET status = ? WHERE job_name = ?",
                (status, job_name)
            )

def store_tsv_data(job_name: str, tsv_data: Dict[str, List[Dict[str, Any]]]):
    """Store TSV data in database"""
    with get_db_cursor() as cursor:
        for file_name, rows in tsv_data.items():
            # Clean up filename for display
            artifact_name = file_name.replace('.tsv', '').replace('_', ' ').title()
            # Insert artifact type metadata
            cursor.execute(
                "INSERT INTO artifact_types (job_name, file_name, artifact_name) VALUES (?, ?, ?)",
                (job_name, file_name, artifact_name)
            )
            artifact_type_id = cursor.lastrowid

            # Store each row as JSON data
            for row_index, row_data in enumerate(rows):
                cursor.execute(
                    "INSERT INTO artifact_data (job_name, artifact_type_id, row_index, data_json) VALUES (?, ?, ?, ?)",
                    (job_name, artifact_type_id, row_index, json.dumps(row_data))
                )

        logger.info(f"Stored TSV data for job {job_name}: {len(tsv_data)} files")

def store_spatial_data(job_name: str, spatial_data: List[Dict[str, Any]]):
    """Store spatial data in database"""
    with get_db_cursor() as cursor:
        for data in spatial_data:
            cursor.execute(
                "INSERT INTO spatial_data (job_name, timestamp, latitude, longitude, activity, source_artifact) VALUES (?, ?, ?, ?, ?, ?)",
                (job_name, data.get('timestamp'), data.get('latitude'), data.get('longitude'),
                 data.get('activity'), data.get('source_artifact'))
            )

        logger.info(f"Stored spatial data for job {job_name}: {len(spatial_data)} locations")

def store_timeline_data(job_name: str, timeline_data: List[Dict[str, Any]]):
    """Store timeline data in database"""
    with get_db_cursor() as cursor:
        for event in timeline_data:
            cursor.execute(
                "INSERT INTO timeline_events (job_name, key, activity, datalist, source_artifact) VALUES (?, ?, ?, ?, ?)",
                (job_name, event.get('key'), event.get('activity'), event.get('datalist'),
                 event.get('source_artifact'))
            )

        logger.info(f"Stored timeline data for job {job_name}: {len(timeline_data)} events")