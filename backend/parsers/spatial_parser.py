import sqlite3 as db
import json
import os
from typing import List, Dict, Any

# Parse LEAPP directory's db into ours
def parse_latlong_db(db_path: str) -> List[Dict[str, Any]]:
    """Parse _latlong.db from KML Exports"""
    if not os.path.exists(db_path):
        return []

    spatial_data = []
    try:
        conn = db.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT timestamp, latitude, longitude, activity FROM data")
        rows = cursor.fetchall()

        for row in rows:
            timestamp, latitude, longitude, activity = row
            spatial_data.append({
                'timestamp': timestamp,
                'latitude': latitude,
                'longitude': longitude,
                'activity': activity,
                'source_artifact': '_latlong.db',
                'metadata_json': json.dumps({
                    'timestamp': timestamp,
                    'latitude': latitude,
                    'longitude': longitude,
                    'activity': activity
                })
            })

        conn.close()
    except Exception as e:
        print(f"Error parsing spatial data: {e}")

    return spatial_data