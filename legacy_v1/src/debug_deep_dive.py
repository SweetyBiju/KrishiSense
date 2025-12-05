import pandas as pd
import os
import re
from src.config import RAW_CROP_DATA, WEATHER_DATA_DIR
# CONFIG
CROP_DATA_PATH = RAW_CROP_DATA
WEATHER_DIR = WEATHER_DATA_DIR
def debug_one_row():
    print(" STARTING DEEP DIVE DEBUG...")
    
    # 1. Load ONE row of Gov Data
    try:
        dfs = pd.read_html(CROP_DATA_PATH, flavor='bs4')
        df = dfs[0]
        
        # Force Column Rename (same as merger script)
        new_columns = list(df.columns)
        new_columns[0] = 'State'
        new_columns[1] = 'District'
        new_columns[2] = 'Year'
        df.columns = new_columns
        
        # Clean Text (The Fix we applied)
        df['State'] = df['State'].astype(str).str.strip().str.replace(r'^\d+\.\s*', '', regex=True)
        df['District'] = df['District'].astype(str).str.strip().str.replace(r'^\d+\.\s*', '', regex=True)
        
        # Grab the first row
        row = df.iloc[0]
        print(f"\n[1] GOV DATA ROW:")
        print(f"    State:    '{row['State']}'")
        print(f"    District: '{row['District']}'")
        print(f"    Year:     '{row['Year']}' (Type: {type(row['Year'])})")
        
    except Exception as e:
        print(f" Failed to load Gov Data: {e}")
        return

    # 2. Construct Filename
    safe_name = f"{row['District']}_{row['State']}".replace(" ", "_").lower()
    expected_file = f"{safe_name}.csv"
    full_path = os.path.join(WEATHER_DIR, expected_file)
    
    print(f"\n[2] LOOKING FOR WEATHER FILE:")
    print(f"    Expected Name: {expected_file}")
    print(f"    Full Path:     {full_path}")
    
    if not os.path.exists(full_path):
        print(f" FAILURE: File does not exist!")
        # List similar files to see if it's a spelling issue
        print("    Listing first 5 files in weather folder for comparison:")
        print(os.listdir(WEATHER_DIR)[:5])
        return
    else:
        print(f" SUCCESS: File found.")

    # 3. Check Data Inside File
    try:
        w_df = pd.read_csv(full_path)
        w_df['Date'] = pd.to_datetime(w_df.iloc[:, 0]) # Use index 0 as Date
        
        print(f"\n[3] CHECKING WEATHER CONTENT:")
        print(f"    Weather Data Min Year: {w_df['Date'].dt.year.min()}")
        print(f"    Weather Data Max Year: {w_df['Date'].dt.year.max()}")
        
        # 4. Attempt Match
        target_year = int(row['Year']) # This might fail if year is "2015-16"
        print(f"    Target Year: {target_year}")
        
        mask = (w_df['Date'].dt.year == target_year)
        matched_data = w_df.loc[mask]
        
        if matched_data.empty:
            print(f" FAILURE: No weather data found for year {target_year}.")
            print(f"    (Maybe the Gov Year format '2015-16' doesn't match Calendar Year?)")
        else:
            print(f" SUCCESS: Found {len(matched_data)} rows of weather data!")
            print(f"    Avg Temp: {matched_data['T2M'].mean()}")

    except Exception as e:
        print(f" FAILURE processing weather CSV: {e}")

if __name__ == "__main__":
    debug_one_row()