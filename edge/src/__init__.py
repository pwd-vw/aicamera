"""
AI Camera Edge Component
License Plate Recognition with Hailo AI Accelerator
"""

__version__ = "2.0.0"
__author__ = "AI Camera Team"
__description__ = "Edge AI Camera for LPR Detection"

# Version information
VERSION_INFO = {
    "version": __version__,
    "component": "edge",
    "language": "python",
    "framework": "flask",
    "ai_accelerator": "hailo-8"
}

def get_version():
    """Get the current version of the edge component."""
    return __version__

def get_version_info():
    """Get detailed version information."""
    return VERSION_INFO.copy()
