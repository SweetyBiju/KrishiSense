import pandas as pd
import os

# Path to your file
FILE_PATH = os.path.join("data", "raw", "gov_crop_data", "crop_production_2015_2023.xls")

print("Loading dataset... (This might take a moment)")

try:
    # Remember: It is an HTML file disguised as XLS
    dfs = pd.read_html(FILE_PATH)
    df = dfs[0] # Get the main table
    
    # 1. Total Rows
    total_rows = len(df)
    
    # 2. Total Columns
    total_cols = len(df.columns)
    
    # 3. Quick Stats
    # We grab column 0 (State) and 1 (District) by index to avoid naming issues
    unique_states = df.iloc[:, 0].nunique()
    unique_districts = df.iloc[:, 1].nunique()
    
    print("-" * 30)
    print(f"📊 DATASET STATISTICS")
    print("-" * 30)
    print(f"Total Rows:        {total_rows:,}")  # The comma adds thousands separator (e.g., 10,000)
    print(f"Total Columns:     {total_cols}")
    print(f"Unique States:     {unique_states}")
    print(f"Unique Districts:  {unique_districts}")
    print("-" * 30)

except Exception as e:
    print(f"Error: {e}")