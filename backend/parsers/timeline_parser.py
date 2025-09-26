import sqlite3 as db
import json
import os
from typing import List, Dict, Any

# Parse LEAPP directory's db into ours
def parse_timeline_db(db_path: str) -> List[Dict[str, Any]]:
    """Parse tl.db from Timeline directory"""
    if not os.path.exists(db_path):
        return []

    timeline_events = []
    try:
        conn = db.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT key, activity, datalist FROM data")
        rows = cursor.fetchall()

        for row in rows:
            key, activity, datalist = row
            timeline_events.append({
                'key': key,
                'activity': activity,
                'datalist': datalist,
                'source_artifact': 'tl.db',
                'metadata_json': json.dumps({
                    'key': key,
                    'activity': activity,
                    'datalist': datalist
                })
            })

        conn.close()
    except Exception as e:
        print(f"Error parsing timeline data: {e}")

    return timeline_events