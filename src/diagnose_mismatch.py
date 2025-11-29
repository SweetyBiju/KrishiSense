import pandas as pd
import os
import re

# CONFIG
CROP_DATA_PATH = os.path.join("data", "raw", "gov_crop_data", "crop_production_2015_2023.xls")
WEATHER_DIR = os.path.join("data", "raw", "nasa_weather")

def diagnose_specific():
    print(" SEARCHING FOR A VALID MATCH (PUNE)...")
    
    # 1. Load Gov Data
    try:
        dfs = pd.read_html(CROP_DATA_PATH)
        df = dfs[0]
        
        # Rename by Index
        new_columns = list(df.columns)
        new_columns[0] = 'State'
        new_columns[1] = 'District'
        new_columns[2] = 'Year'
        df.columns = new_columns
        
        # Clean
        df['State'] = df['State'].astype(str).str.strip().str.replace(r'^\d+\.\s*', '', regex=True)
        df['District'] = df['District'].astype(str).str.strip().str.replace(r'^\d+\.\s*', '', regex=True)
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 2. Get Files
    if not os.path.exists(WEATHER_DIR): return
    actual_files = set(os.listdir(WEATHER_DIR))

    # 3. Find Pune (or any existing district)
    # We filter the dataframe to find a row where District contains "Pune"
    target_row = df[df['District'].str.contains("Pune", case=False, na=False)].iloc[0]
    
    if target_row.empty:
        print("Could not find Pune in Gov Data.")
        return

    raw_state = target_row['State']
    raw_dist = target_row['District']
    
    # Construct Filename
    target_name = f"{raw_dist}_{raw_state}".replace(" ", "_").lower()
    target_file = f"{target_name}.csv"
    
    print(f"\nTarget Gov Row:")
    print(f"   State:    '{raw_state}'")
    print(f"   District: '{raw_dist}'")
    print(f"   Looking for file: [{target_file}]")
    
    if target_file in actual_files:
        print("\n MATCH CONFIRMED! The naming logic is correct.")
        print("   The issue must be in the YEAR matching.")
    else:
        print("\n STILL NO MATCH. Naming logic is broken for Pune too.")

if __name__ == "__main__":
    diagnose_specific()