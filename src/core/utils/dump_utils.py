import json
import os
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger("dump_utils")

TMP_DIR = "/tmp/villmprep"


def _ensure_tmp_dir():
    """Ensure the tmp directory exists."""
    os.makedirs(TMP_DIR, exist_ok=True)


def save_to_tmp(data: Any, prefix: str) -> str:
    """
    Save data to a timestamped JSON file in /tmp/villmprep/.
    
    Args:
        data: Data to save (must be JSON-serializable).
        prefix: Prefix for the filename (e.g., 'keywords', 'questions').
    
    Returns:
        The filepath of the saved file, or empty string on failure.
    """
    try:
        _ensure_tmp_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{prefix}_{timestamp}.json"
        filepath = os.path.join(TMP_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dumped data to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to dump data to tmp: {e}")
        return ""


def load_from_tmp(filepath: str) -> Any:
    """
    Load data from a JSON file in /tmp/villmprep/.
    
    Args:
        filepath: Full path to the file to load.
    
    Returns:
        The loaded data, or None on failure.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded data from {filepath}")
        return data
    except Exception as e:
        logger.error(f"Failed to load data from {filepath}: {e}")
        return None


def list_tmp_files(prefix: str = "") -> list:
    """
    List saved tmp files, optionally filtered by prefix.
    
    Args:
        prefix: Optional prefix to filter files.
    
    Returns:
        List of filepaths matching the prefix.
    """
    try:
        _ensure_tmp_dir()
        files = os.listdir(TMP_DIR)
        if prefix:
            files = [f for f in files if f.startswith(prefix)]
        return [os.path.join(TMP_DIR, f) for f in sorted(files)]
    except Exception as e:
        logger.error(f"Failed to list tmp files: {e}")
        return []