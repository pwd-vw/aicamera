#! /usr/bin/env python3
"""
Edge Component Version Update Script

This script updates the edge component version information according to the
semantic versioning strategy defined in docs/project/versioning.md.

Author: AI Camera Team
Version: 2.0.0
"""

import os
import sys
import re
import yaml
from pathlib import Path
from datetime import datetime

def get_current_version():
    """Get current version from server package.json."""
    package_json = Path(__file__).parent.parent.parent / 'server' / 'package.json'
    if not package_json.exists():
        print(f"Error: package.json not found at {package_json}")
        return "2.0.0"  # Default fallback
    
    import json
    with open(package_json, 'r') as f:
        data = json.load(f)
        return data.get('version', '2.0.0')

def update_python_files(version):
    """Update version information in Python files."""
    edge_dir = Path(__file__).parent.parent
    
    # Files to update
    files_to_update = [
        edge_dir / 'src' / 'app.py',
        edge_dir / 'src' / 'web' / 'blueprints' / 'camera.py',
        edge_dir / 'src' / 'web' / 'blueprints' / '__init__.py',
    ]
    
    for file_path in files_to_update:
        if file_path.exists():
            update_file_version(file_path, version)

def update_file_version(file_path, version):
    """Update version in a specific file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update version in docstrings
        content = re.sub(
            r'Version: \d+\.\d+\.\d+',
            f'Version: {version}',
            content
        )
        
        # Update version in comments
        content = re.sub(
            r'AI Camera v\d+\.\d+\.\d+',
            f'AI Camera v{version}',
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Updated version in {file_path}")
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def update_js_files(version):
    """Update version information in JavaScript files."""
    edge_dir = Path(__file__).parent.parent
    
    # Files to update
    files_to_update = [
        edge_dir / 'src' / 'web' / 'static' / 'js' / 'camera.js',
    ]
    
    for file_path in files_to_update:
        if file_path.exists():
            update_js_file_version(file_path, version)

def update_js_file_version(file_path, version):
    """Update version in a JavaScript file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update version in comments
        content = re.sub(
            r'AI Camera v\d+\.\d+\.\d+',
            f'AI Camera v{version}',
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Updated version in {file_path}")
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def update_documentation(version):
    """Update version information in documentation files."""
    docs_dir = Path(__file__).parent.parent.parent / 'docs'
    
    # Files to update
    files_to_update = [
        docs_dir / 'edge' / 'api-reference.md',
    ]
    
    for file_path in files_to_update:
        if file_path.exists():
            update_doc_version(file_path, version)

def update_doc_version(file_path, version):
    """Update version in a documentation file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update version in headers
        content = re.sub(
            r'\*\*Version:\*\* \d+\.\d+\.\d+',
            f'**Version:** {version}',
            content
        )
        
        # Update version in examples
        content = re.sub(
            r'"version": "\d+\.\d+\.\d+"',
            f'"version": "{version}"',
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Updated version in {file_path}")
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def main():
    """Main function to update edge component version."""
    print("🔄 Updating Edge Component Version...")
    
    # Get current version from package.json
    version = get_current_version()
    print(f"📋 Current version: {version}")
    
    # Update Python files
    print("🐍 Updating Python files...")
    update_python_files(version)
    
    # Update JavaScript files
    print("📜 Updating JavaScript files...")
    update_js_files(version)
    
    # Update documentation
    print("📚 Updating documentation...")
    update_documentation(version)
    
    print(f"✅ Edge component version updated to {version}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
