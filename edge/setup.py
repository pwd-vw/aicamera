#!/usr/bin/env python3
"""
Setup script for AI Camera Edge Component
Note: This is primarily for development/testing. Production deployment uses:
- edge/installation/install.sh for installation
- systemd service (aicamera_v1.3.service)
- nginx on port 80 → gunicorn unix socket → wsgi.py
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AI Camera Edge Component"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="aicamera-edge",
    version="2.0.0",
    description="AI Camera Edge Component - License Plate Recognition with Hailo AI Accelerator",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="AI Camera Team",
    author_email="team@aicamera.com",
    url="https://github.com/popwandee/aicamera",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video :: Capture",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aicamera-edge=src.app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
