import os
import sqlite3
from typing import List, Dict, Any

def parse_leapp_db(db_path: str, query: str, field_mapping: List[str], source_artifact: str) -> List[Dict[str, Any]]:
    """Parse LEAPP database with flexible query and field mapping"""
    if not os.path.exists(db_path):
        return []

    data = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            data.append({
                field: row[i]
                for i, field in enumerate(field_mapping)
            })
            data[-1]['source_artifact'] = source_artifact

        conn.close()
    except Exception as e:
        print(f"Error parsing {source_artifact} data: {e}")

    return data

def parse_timeline_db(db_path: str) -> List[Dict[str, Any]]:
    """Parse LEAPP's TL database into ours"""
    return parse_leapp_db(
        db_path=db_path,
        query="SELECT key, activity, datalist FROM data",
        field_mapping=['key', 'activity', 'datalist'],
        source_artifact='tl.db'
    )

def parse_spatial_db(db_path: str) -> List[Dict[str, Any]]:
    """Parse LEAPP's KML database into ours"""
    return parse_leapp_db(
        db_path=db_path,
        query="SELECT timestamp, latitude, longitude, activity FROM data",
        field_mapping=['timestamp', 'latitude', 'longitude', 'activity'],
        source_artifact='_latlong.db'
    )