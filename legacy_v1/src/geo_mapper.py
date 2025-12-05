import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
import os
import re  # Added for removing numbers like "1. "

from src.config import RAW_CROP_DATA, DISTRICT_MAPPING

# ==========================================
# CONFIGURATION (Updated with your filenames)
# ==========================================
# Input File
RAW_DATA_PATH = RAW_CROP_DATA
# Output File
OUTPUT_PATH = DISTRICT_MAPPING

# ==========================================
# LOGIC
# ==========================================
def clean_text(text):
    """
    Removes leading numbers and dots.
    Example: "1. Andaman" -> "Andaman"
    """
    if not isinstance(text, str):
        return str(text)
    # Regex: Remove leading digits followed by a dot and space
    return re.sub(r'^\d+\.\s*', '', text).strip()

def extract_unique_locations(file_path):
    print(f"[INFO] Reading raw data from {file_path}...")
    try:
        # Parse HTML
        dfs = pd.read_html(file_path)
        if not dfs:
            raise ValueError("No data tables found.")
            
        df = dfs[0]
        
        # Extract Col 0 (State) and Col 1 (District)
        print("[INFO] Cleaning State and District names...")
        locations = df.iloc[:, [0, 1]].copy()
        locations.columns = ['state_name', 'district_name']
        
        # Basic cleanup
        locations = locations.dropna()
        locations = locations[locations['district_name'].astype(str).str.lower() != 'total']
        locations = locations[locations['state_name'].astype(str).str.lower() != 'state']

        # === NEW: Remove the "1. ", "2. " prefixes ===
        locations['state_name'] = locations['state_name'].apply(clean_text)
        locations['district_name'] = locations['district_name'].apply(clean_text)

        # Remove duplicates
        locations = locations.drop_duplicates().reset_index(drop=True)
        
        print(f"[SUCCESS] Found {len(locations)} unique districts after cleaning.")
        print(f"[DEBUG] Sample Data:\n{locations.head()}")
        
        return locations

    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
        return None

def fetch_coordinates(locations_df):
    # Check if we need to resume (handle empty file case)
    if os.path.exists(OUTPUT_PATH):
        try:
            existing_df = pd.read_csv(OUTPUT_PATH)
            if existing_df.empty:
                processed_keys = set()
            else:
                print("[INFO] Resuming from existing file...")
                processed_keys = set(existing_df['district_name'] + "_" + existing_df['state_name'])
        except pd.errors.EmptyDataError:
            # File exists but is empty
            processed_keys = set()
    else:
        processed_keys = set()

    # Setup Geocoder
    geolocator = Nominatim(user_agent="agrifusion_project_student_v2")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.0)

    new_rows = []
    
    print(f"[INFO] Starting Geocoding for {len(locations_df)} districts...")
    
    # Use tqdm for progress bar
    for index, row in tqdm(locations_df.iterrows(), total=locations_df.shape[0]):
        state = row['state_name']
        district = row['district_name']
        unique_key = f"{district}_{state}"

        if unique_key in processed_keys:
            continue

        query = f"{district}, {state}, India"
        
        try:
            location = geocode(query)
            if location:
                new_rows.append({
                    'state_name': state,
                    'district_name': district,
                    'latitude': location.latitude,
                    'longitude': location.longitude
                })
            else:
                new_rows.append({
                    'state_name': state,
                    'district_name': district,
                    'latitude': None,
                    'longitude': None
                })
                
        except Exception as e:
            print(f"[WARN] Error for {query}: {e}")

        # Save batch every 10 rows
        if len(new_rows) >= 10:
            temp_df = pd.DataFrame(new_rows)
            mode = 'a' if os.path.exists(OUTPUT_PATH) else 'w'
            header = not os.path.exists(OUTPUT_PATH)
            temp_df.to_csv(OUTPUT_PATH, mode=mode, header=header, index=False)
            new_rows = []

    # Final Save
    if new_rows:
        temp_df = pd.DataFrame(new_rows)
        mode = 'a' if os.path.exists(OUTPUT_PATH) else 'w'
        header = not os.path.exists(OUTPUT_PATH)
        temp_df.to_csv(OUTPUT_PATH, mode=mode, header=header, index=False)

    print(f"[DONE] Coordinates saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    locs = extract_unique_locations(RAW_DATA_PATH)
    if locs is not None:
        fetch_coordinates(locs)