"""
Pipeline runner script for Carbon Footprint Analysis of Electricity Generation Sources.
Executes the full ingestion, cleaning, normalization, metric calculation, validation, and export process.
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_processing import run_full_pipeline

def main():
    print("==================================================")
    print("   Starting Carbon Footprint Data Pipeline       ")
    print("==================================================")
    try:
        df_clean = run_full_pipeline()
        print(f"\n[SUCCESS] Pipeline executed successfully! Clean rows: {len(df_clean)}")
    except Exception as e:
        print(f"\n[FATAL ERROR] Pipeline execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
