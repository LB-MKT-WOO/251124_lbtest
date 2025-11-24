"""Main entry point for the performance dashboard.
Run with: streamlit run performance_dashboard/main.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to Python path so we can import performance_dashboard as a package
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from performance_dashboard.app import run_dashboard

if __name__ == "__main__":
    run_dashboard()

