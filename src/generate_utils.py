#!/usr/bin/env python3
"""
Shared utilities for SFT and DPO generation scripts.
Handles intermediate file save/load for resume capability.
"""

import json
import os
from typing import Any, Optional

from src.schemas.schemas import ChunkItem


def step_file_path(output_dir: str, step_name: str) -> str:
    """Return the file path for a given step's intermediate data."""
    return os.path.join(output_dir, f"{step_name}.json")


def step_exists(output_dir: str, step_name: str) -> bool:
    """Check if an intermediate file for the given step already exists."""
    return os.path.exists(step_file_path(output_dir, step_name))


def save_intermediate(data: Any, output_dir: str, step_name: str) -> str:
    """
    Save intermediate data to a JSON file in the output directory.
    Creates the output directory if it doesn't exist.
    Returns the file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    path = step_file_path(output_dir, step_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return path


def load_intermediate(output_dir: str, step_name: str) -> Optional[Any]:
    """
    Load intermediate data if it exists, otherwise return None.
    """
    path = step_file_path(output_dir, step_name)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_chunks(input_path: str) -> list[ChunkItem]:
    """
    Load chunk data from a JSON file.

    Expected format (list of dicts):
        [
            {
                "chunk_id": "0",
                "parent_id": "source_doc_id",
                "content": "Chunk content text...",
                "domain": "Domain name"
            },
            ...
        ]

    Also supports JSONL format (one JSON object per line).
    """
    chunks = []
    with open(input_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
        if raw.startswith("["):
            data = json.loads(raw)
            for item in data:
                chunks.append(ChunkItem(**item))
        else:
            lines = raw.splitlines()
            for line in lines:
                line = line.strip()
                if line:
                    item = json.loads(line)
                    chunks.append(ChunkItem(**item))
    return chunks


def load_chunks_from_dir(input_dir: str) -> list[ChunkItem]:
    """
    Load chunk data from all JSON/JSONL files in a directory.

    Files are processed in sorted order and concatenated.
    """
    chunks = []
    for name in sorted(os.listdir(input_dir)):
        if name.lower().endswith((".json", ".jsonl")):
            file_path = os.path.join(input_dir, name)
            if os.path.isfile(file_path):
                chunks.extend(load_chunks(file_path))
    return chunks


def check_step(output_dir: str, step_name: str, description: str) -> Optional[Any]:
    """
    Check if a step is already completed. If yes, load and return its data.
    If not, return None so the caller knows to run the step.
    """
    if step_exists(output_dir, step_name):
        print(f"[SKIP] {description} already completed. Loading from {step_file_path(output_dir, step_name)}")
        return load_intermediate(output_dir, step_name)
    return None