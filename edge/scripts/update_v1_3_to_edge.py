#!/usr/bin/env python3
"""
Script to update all v1_3 references to edge in Python files

This script recursively finds all Python files in the edge directory
and replaces all occurrences of 'v1_3' with 'edge' in import statements.
"""

import os
import re
from pathlib import Path

def update_file(file_path):
    """Update a single file by replacing v1_3 with edge in import statements."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace v1_3 with edge in import statements
        # This regex matches import statements that contain v1_3
        updated_content = re.sub(
            r'from\s+v1_3\.',
            'from edge.',
            content
        )
        updated_content = re.sub(
            r'import\s+v1_3\.',
            'import edge.',
            content
        )
        
        # Also replace any remaining v1_3 references in strings or comments
        updated_content = updated_content.replace('v1_3', 'edge')
        
        # Write back to file if content changed
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all Python files in the edge directory."""
    edge_dir = Path('edge')
    
    if not edge_dir.exists():
        print("Edge directory not found!")
        return
    
    # Find all Python files in the edge directory
    python_files = list(edge_dir.rglob('*.py'))
    
    print(f"Found {len(python_files)} Python files to update")
    
    updated_count = 0
    for file_path in python_files:
        if update_file(file_path):
            updated_count += 1
    
    print(f"\nUpdated {updated_count} files out of {len(python_files)} total files")

if __name__ == '__main__':
    main()
