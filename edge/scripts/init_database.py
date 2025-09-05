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

    # detection_results - Minimal schema using only original_image_path for image storage
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS detection_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            vehicles_count INTEGER DEFAULT 0,
            plates_count INTEGER DEFAULT 0,
            ocr_results TEXT,
            original_image_path TEXT,
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

    # Ensure extended OCR columns exist; do not add legacy image path columns
    cur.execute("PRAGMA table_info(detection_results)")
    existing_columns = {row[1] for row in cur.fetchall()}
    extended_columns_sql = {
        'hailo_ocr_results': 'TEXT',
        'easyocr_results': 'TEXT',
        'best_ocr_method': 'TEXT',
        'ocr_processing_time_ms': 'REAL DEFAULT 0.0',
        'parallel_ocr_success': 'BOOLEAN DEFAULT 0',
        'hailo_ocr_confidence': 'REAL DEFAULT 0.0',
        'easyocr_confidence': 'REAL DEFAULT 0.0',
        'hailo_processing_time_ms': 'REAL DEFAULT 0.0',
        'easyocr_processing_time_ms': 'REAL DEFAULT 0.0',
        'hailo_ocr_error': 'TEXT',
        'easyocr_error': 'TEXT'
    }
    for col, decl in extended_columns_sql.items():
        if col not in existing_columns:
            cur.execute(f"ALTER TABLE detection_results ADD COLUMN {col} {decl}")

    # If legacy image path columns exist, rebuild table to drop them (SQLite lacks DROP COLUMN)
    deprecated_cols = {
        'annotated_image_path', 'image_path', 'vehicle_detected_image_path', 'plate_image_path', 'cropped_plates_paths'
    }
    if existing_columns & deprecated_cols:
        desired_cols_order = [
            'id','timestamp','vehicles_count','plates_count','ocr_results','original_image_path',
            'vehicle_detections','plate_detections','processing_time_ms','created_at','sent_to_server',
            'sent_at','server_response','hailo_ocr_results','easyocr_results','best_ocr_method',
            'ocr_processing_time_ms','parallel_ocr_success','hailo_ocr_confidence','easyocr_confidence',
            'hailo_processing_time_ms','easyocr_processing_time_ms','hailo_ocr_error','easyocr_error'
        ]
        # Build CREATE TABLE for new table
        create_sql = """
        CREATE TABLE IF NOT EXISTS detection_results_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            vehicles_count INTEGER DEFAULT 0,
            plates_count INTEGER DEFAULT 0,
            ocr_results TEXT,
            original_image_path TEXT,
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
        cur.execute("BEGIN")
        cur.execute(create_sql)
        # Compute intersection for SELECT
        cur.execute("PRAGMA table_info(detection_results)")
        existing_columns = {row[1] for row in cur.fetchall()}
        copy_cols = [c for c in desired_cols_order if c in existing_columns]
        cols_csv = ",".join(copy_cols)
        cur.execute(f"INSERT INTO detection_results_new ({cols_csv}) SELECT {cols_csv} FROM detection_results")
        cur.execute("DROP TABLE detection_results")
        cur.execute("ALTER TABLE detection_results_new RENAME TO detection_results")
        cur.execute("COMMIT")

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


