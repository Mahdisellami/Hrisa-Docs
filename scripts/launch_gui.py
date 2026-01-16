#!/usr/bin/env python3
"""Launch Document Processor GUI."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.docprocessor.gui.main_window import main

if __name__ == "__main__":
    main()
