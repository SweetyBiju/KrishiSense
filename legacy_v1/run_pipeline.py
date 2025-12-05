import sys
import os

# Add src to python path so imports work correctly
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src import geo_mapper
from src import weather_fetcher
from legacy_v1 import data_merger
from src import clean_and_split
from src.config import RAW_CROP_DATA

def run():
    print("===================================================")
    print("   KRISHISENSE: END-TO-END DATA PIPELINE v1.0")
    print("===================================================")

    # Step 1: Geocoding
    print("\n[STEP 1/4] Checking Geocoding...")
    # We call extract just to verify file access, actual fetch is cached
    locs = geo_mapper.extract_unique_locations(RAW_CROP_DATA)
    if locs is not None:
        geo_mapper.fetch_coordinates(locs)
    
    # Step 2: Weather Fetching
    print("\n[STEP 2/4] Checking NASA Weather Data...")
    # Attempts to find the main function in weather_fetcher
    if hasattr(weather_fetcher, 'process_weather_data'):
         weather_fetcher.process_weather_data()
    elif hasattr(weather_fetcher, 'fetch_weather'):
         weather_fetcher.fetch_weather()
    else:
        print("[WARN] Could not identify main function in weather_fetcher.")

    # Step 3: Merging
    print("\n[STEP 3/4] Merging Government & Weather Data...")
    data_merger.merge_data()

    # Step 4: Preprocessing
    print("\n[STEP 4/4] Cleaning & Splitting for Models...")
    clean_and_split.clean_and_split()

    print("\n===================================================")
    print("   PIPELINE COMPLETE. READY FOR MODELING.")
    print("===================================================")

if __name__ == "__main__":
    run()