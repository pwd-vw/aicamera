#!/usr/bin/env python3
"""
Configuration Blueprint for AI Camera

Provides a simple UI to view/update application configuration and persist
settings to edge/installation/.env.production, with basic error handling.
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash

from edge.src.core.utils.logging_config import get_logger
from edge.src.core import config as app_config


logger = get_logger(__name__)

config_bp = Blueprint('config', __name__, url_prefix='/config')


ENV_FILE_PATH = Path(app_config.BASE_DIR) / 'edge' / 'installation' / '.env.production'


def _parse_env_file(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    try:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    data[key.strip()] = value.strip().strip('\"\'')
    except Exception as exc:
        logger.error(f"Failed to parse env file {path}: {exc}")
    return data


def _load_current_values() -> Dict[str, str]:
    """Return a dict of config keys for the form, preferring .env.production values."""
    env_values = _parse_env_file(ENV_FILE_PATH)

    # Base defaults from current runtime/config
    defaults = {
        'SERVER_URL': os.getenv('SERVER_URL', 'http://localhost:3000'),
        'WEBSOCKET_SERVER_URL': os.getenv('WEBSOCKET_SERVER_URL', ''),
        'AICAMERA_ID': os.getenv('AICAMERA_ID', app_config.AICAMERA_ID),
        'CHECKPOINT_ID': os.getenv('CHECKPOINT_ID', app_config.CHECKPOINT_ID),
        'MAIN_RESOLUTION': 'x'.join(map(str, app_config.MAIN_RESOLUTION)),
        'LORES_RESOLUTION': 'x'.join(map(str, app_config.LORES_RESOLUTION)),
        'CAMERA_FPS': str(app_config.DEFAULT_FRAMERATE),
        'MQTT_ENABLED': os.getenv('MQTT_ENABLED', 'true'),
        'MQTT_BROKER_HOST': os.getenv('MQTT_BROKER_HOST', 'localhost'),
        'MQTT_BROKER_PORT': os.getenv('MQTT_BROKER_PORT', '1883'),
        'MQTT_USERNAME': os.getenv('MQTT_USERNAME', ''),
        'MQTT_PASSWORD': os.getenv('MQTT_PASSWORD', ''),
    }

    # Merge, giving precedence to env file values
    merged = defaults.copy()
    for k in list(defaults.keys()):
        if k in env_values and env_values[k] != '':
            merged[k] = env_values[k]

    return merged


def _write_env_file(data: Dict[str, str]) -> None:
    """Safely write key=value pairs to .env.production with backup."""
    ENV_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if ENV_FILE_PATH.exists():
        backup_path = ENV_FILE_PATH.with_suffix(f".backup_{int(datetime.now().timestamp())}")
        shutil.copy2(ENV_FILE_PATH, backup_path)
        logger.info(f"Backed up existing env to {backup_path}")

    lines = []
    for key, value in data.items():
        # Escape any newlines or quotes
        if value is None:
            value = ''
        safe = str(value).replace('\n', ' ').strip()
        lines.append(f"{key}={safe}")

    tmp_path = ENV_FILE_PATH.with_suffix('.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    os.replace(tmp_path, ENV_FILE_PATH)


def _restart_service() -> bool:
    """Attempt to restart the aicamera_lpr.service; return success flag."""
    try:
        result = subprocess.run(
            ['sudo', 'systemctl', 'restart', 'aicamera_lpr.service'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            logger.error(f"Service restart failed: {result.stderr}")
            return False
        return True
    except Exception as exc:
        logger.error(f"Service restart exception: {exc}")
        return False


@config_bp.route('/', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        try:
            # Collect fields from the form
            payload = {
                'SERVER_URL': request.form.get('SERVER_URL', '').strip(),
                'WEBSOCKET_SERVER_URL': request.form.get('WEBSOCKET_SERVER_URL', '').strip(),
                'AICAMERA_ID': request.form.get('AICAMERA_ID', '').strip(),
                'CHECKPOINT_ID': request.form.get('CHECKPOINT_ID', '').strip(),
                'MAIN_RESOLUTION': request.form.get('MAIN_RESOLUTION', '').strip(),
                'LORES_RESOLUTION': request.form.get('LORES_RESOLUTION', '').strip(),
                'CAMERA_FPS': request.form.get('CAMERA_FPS', '').strip(),
                'MQTT_ENABLED': request.form.get('MQTT_ENABLED', 'false'),
                'MQTT_BROKER_HOST': request.form.get('MQTT_BROKER_HOST', '').strip(),
                'MQTT_BROKER_PORT': request.form.get('MQTT_BROKER_PORT', '').strip(),
                'MQTT_USERNAME': request.form.get('MQTT_USERNAME', '').strip(),
                'MQTT_PASSWORD': request.form.get('MQTT_PASSWORD', '').strip(),
            }

            # Basic validation
            if not payload['AICAMERA_ID']:
                flash('AICAMERA_ID is required', 'danger')
                return render_template('config/setup.html', values=payload)

            # Write env file
            _write_env_file(payload)

            # Try restarting service
            ok = _restart_service()
            if ok:
                flash('Configuration saved and service restarted successfully.', 'success')
            else:
                flash('Configuration saved. Failed to restart service automatically. Please restart manually.', 'warning')

            return redirect(url_for('config.setup'))

        except Exception as exc:
            logger.error(f"Config setup error: {exc}")
            flash(f"Error saving configuration: {exc}", 'danger')
            return render_template('config/setup.html', values=_load_current_values()), 500

    # GET
    return render_template('config/setup.html', values=_load_current_values())


def register_config_events(socketio):
    # No Socket.IO events for this page currently
    return None


