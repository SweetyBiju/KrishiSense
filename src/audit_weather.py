import pandas as pd
import os

# ==========================================
# CONFIGURATION
# ==========================================
MAPPING_FILE = os.path.join("data", "interim", "district_mapping.csv")
WEATHER_DIR = os.path.join("data", "raw", "nasa_weather")

def audit_data():
    print(f" Starting Data Audit...")
    print(f"Checking Mapping File: {MAPPING_FILE}")
    print(f"Checking Weather Folder: {WEATHER_DIR}")
    print("-" * 40)

    if not os.path.exists(MAPPING_FILE):
        print(" CRITICAL ERROR: district_mapping.csv not found.")
        return

    # Load the target list
    df = pd.read_csv(MAPPING_FILE)
    
    total_districts = len(df)
    missing_coords = 0
    downloaded_files = 0
    missing_downloads = []

    print(f"Total Districts in Government Data: {total_districts}")

    # Loop through and check
    for index, row in df.iterrows():
        district = str(row['district_name'])
        state = str(row['state_name'])
        
        # 1. Check if we even have coordinates (GeoMapper success/fail)
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            missing_coords += 1
            continue # We couldn't download this anyway

        # 2. Check if the file exists (WeatherFetcher success/fail)
        # Reconstruct the exact filename logic used in weather_fetcher.py
        safe_name = f"{district}_{state}".replace(" ", "_").lower()
        expected_filename = f"{safe_name}.csv"
        file_path = os.path.join(WEATHER_DIR, expected_filename)

        if os.path.exists(file_path):
            downloaded_files += 1
        else:
            missing_downloads.append(f"{district} ({state})")

    # ==========================================
    # FINAL REPORT
    # ==========================================
    print("-" * 40)
    print(" AUDIT RESULTS")
    print("-" * 40)
    print(f" Successfully Downloaded:    {downloaded_files}")
    print(f"  Skipped (No Coordinates):    {missing_coords} (GeoMapper couldn't find these)")
    print(f" Missing (Download Failed):    {len(missing_downloads)} (Network/API errors)")
    print("-" * 40)
    
    completion_rate = (downloaded_files / total_districts) * 100
    print(f" Project Readiness: {completion_rate:.2f}%")

    if missing_downloads:
        print("\n List of Missing Downloads (Try running weather_fetcher.py again):")
        for d in missing_downloads[:10]: # Print first 10 only
            print(f" - {d}")
        if len(missing_downloads) > 10:
            print(f" ... and {len(missing_downloads) - 10} more.")

if __name__ == "__main__":
    audit_data()