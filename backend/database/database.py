import sqlite3
import json
import os
from typing import Dict, List, Any

# Database setup and utility functions for LEAPP forensic data storage

def init_database():
    """Initialize SQLite database with validated schema"""
    # Create database file in same directory as this script
    db_path = os.path.join(os.path.dirname(__file__), "leapp_forensics.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Main report metadata table: stores info about each uploaded report
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT UNIQUE NOT NULL,         -- Unique identifier for each report job
            report_path TEXT NOT NULL,              -- File system path to the report directory
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'processing',      -- processing/completed/failed
            total_files INTEGER DEFAULT 0,         -- Total files to process
            processed_files INTEGER DEFAULT 0,     -- Files processed so far
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
            row_count INTEGER DEFAULT 0,          -- Number of data rows in this TSV
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
            metadata_json TEXT,                     -- Additional data as JSON
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
            metadata_json TEXT,                     -- Extra event data as JSON
            FOREIGN KEY (job_name) REFERENCES reports(job_name) ON DELETE CASCADE
        )
    ''')

    # Save changes and close connection
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    # Return connection to the SQLite database file
    return sqlite3.connect(os.path.join(os.path.dirname(__file__), "leapp_forensics.db"))

def insert_report_metadata(job_name: str, report_path: str):
    """Insert report metadata"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Add new report with 'processing' status
    cursor.execute(
        "INSERT INTO reports (job_name, report_path, status) VALUES (?, ?, 'processing')",
        (job_name, report_path)
    )
    conn.commit()
    conn.close()

def update_report_status(job_name: str, status: str, error_message: str = None):
    """Update report processing status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Update status and optionally include error message
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
    conn.commit()
    conn.close()

def store_tsv_data(job_name: str, tsv_data: Dict[str, List[Dict[str, Any]]]):
    """Store TSV data in database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Process each TSV file's data
    for file_name, rows in tsv_data.items():
        # Clean up filename for display
        artifact_name = file_name.replace('.tsv', '').replace('_', ' ').title()
        # Insert artifact type metadata
        cursor.execute(
            "INSERT INTO artifact_types (job_name, file_name, artifact_name, row_count) VALUES (?, ?, ?, ?)",
            (job_name, file_name, artifact_name, len(rows))
        )
        artifact_type_id = cursor.lastrowid

        # Store each row as JSON data
        for row_index, row_data in enumerate(rows):
            cursor.execute(
                "INSERT INTO artifact_data (job_name, artifact_type_id, row_index, data_json) VALUES (?, ?, ?, ?)",
                (job_name, artifact_type_id, row_index, json.dumps(row_data))
            )

    conn.commit()
    conn.close()

def store_spatial_data(job_name: str, spatial_data: List[Dict[str, Any]]):
    """Store spatial data in database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert each spatial data point (GPS coordinates, timestamps, etc.)
    for data in spatial_data:
        cursor.execute(
            "INSERT INTO spatial_data (job_name, timestamp, latitude, longitude, activity, source_artifact, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (job_name, data.get('timestamp'), data.get('latitude'), data.get('longitude'),
             data.get('activity'), data.get('source_artifact'), data.get('metadata_json'))
        )

    conn.commit()
    conn.close()

def store_timeline_data(job_name: str, timeline_data: List[Dict[str, Any]]):
    """Store timeline data in database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert each timeline event
    for event in timeline_data:
        cursor.execute(
            "INSERT INTO timeline_events (job_name, key, activity, datalist, source_artifact, metadata_json) VALUES (?, ?, ?, ?, ?, ?)",
            (job_name, event.get('key'), event.get('activity'), event.get('datalist'),
             event.get('source_artifact'), event.get('metadata_json'))
        )

    conn.commit()
    conn.close()