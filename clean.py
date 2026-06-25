#!/usr/bin/env python3
"""
clean.py  —  PyTabletop Engine  —  Project Cleaner
===================================================
Removes all temporary and compiled Python files from the project:
  - __pycache__/ folders
  - *.pyc compiled bytecode
  - *.pyo optimised bytecode
  - .DS_Store (macOS metadata)
  - Thumbs.db (Windows thumbnail cache)

Run from the project root:
    python clean.py
"""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parent

REMOVE_DIRS  = {"__pycache__"}
REMOVE_FILES = {".DS_Store", "Thumbs.db"}
REMOVE_EXTS  = {".pyc", ".pyo"}

def clean(root: Path) -> None:
    removed_dirs  = 0
    removed_files = 0

    for path in sorted(root.rglob("*"), reverse=True):   # deepest first
        if path.is_dir() and path.name in REMOVE_DIRS:
            shutil.rmtree(path)
            print(f"  🗑️  Removed dir  : {path.relative_to(root)}")
            removed_dirs += 1

        elif path.is_file():
            if path.name in REMOVE_FILES or path.suffix in REMOVE_EXTS:
                path.unlink()
                print(f"  🗑️  Removed file : {path.relative_to(root)}")
                removed_files += 1

    print()
    if removed_dirs + removed_files == 0:
        print("  ✅  Already clean — nothing to remove.")
    else:
        print(f"  ✅  Done!  Removed {removed_dirs} director{'y' if removed_dirs==1 else 'ies'}"
              f" and {removed_files} file{'s' if removed_files!=1 else ''}.")

if __name__ == "__main__":
    print("\n" + "═" * 44)
    print("  PyTabletop Engine — Project Cleaner")
    print("═" * 44)
    clean(ROOT)
    print("═" * 44 + "\n")
