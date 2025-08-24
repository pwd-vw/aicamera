#!/usr/bin/env python3
"""
Initialize SQLite database schema for AI Camera v1.3.
This script creates all required tables and indexes for a clean install.
Run before starting the service to avoid runtime schema migrations.
"""

import sqlite3
from pathlib import Path
import sys

try:
    from edge.src.core.config import DATABASE_PATH
except Exception:
    DATABASE_PATH = "db/lpr_data.db"


def main() -> int:
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # detection_results
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS detection_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            vehicles_count INTEGER DEFAULT 0,
            plates_count INTEGER DEFAULT 0,
            ocr_results TEXT,
            original_image_path TEXT,
            vehicle_detected_image_path TEXT,
            plate_image_path TEXT,
            cropped_plates_paths TEXT,
            vehicle_detections TEXT,
            plate_detections TEXT,
            processing_time_ms REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            sent_to_server BOOLEAN DEFAULT 0,
            sent_at DATETIME,
            server_response TEXT,
            hailo_ocr_results TEXT DEFAULT NULL,
            easyocr_results TEXT DEFAULT NULL,
            best_ocr_method TEXT DEFAULT NULL,
            ocr_processing_time_ms REAL DEFAULT 0.0,
            parallel_ocr_success BOOLEAN DEFAULT 0,
            hailo_ocr_confidence REAL DEFAULT 0.0,
            easyocr_confidence REAL DEFAULT 0.0,
            hailo_processing_time_ms REAL DEFAULT 0.0,
            easyocr_processing_time_ms REAL DEFAULT 0.0,
            hailo_ocr_error TEXT DEFAULT NULL,
            easyocr_error TEXT DEFAULT NULL
        )
        """
    )

    # system_events
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # configuration
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS configuration (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # health_checks
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS health_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            component TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            sent_to_server BOOLEAN DEFAULT 0,
            sent_at DATETIME,
            server_response TEXT
        )
        """
    )

    # websocket_sender_logs
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS websocket_sender_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            data_type TEXT,
            record_count INTEGER DEFAULT 0,
            server_response TEXT,
            aicamera_id TEXT,
            checkpoint_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Indexes (idempotent)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_detection_sent_to_server ON detection_results(sent_to_server)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_health_sent_to_server ON health_checks(sent_to_server)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_websocket_logs_timestamp ON websocket_sender_logs(timestamp)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_websocket_logs_action ON websocket_sender_logs(action)"
    )

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


