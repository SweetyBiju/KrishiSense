import pandas as pd
import os
from tqdm import tqdm


from src.config import RAW_CROP_DATA, WEATHER_DATA_DIR,MASTER_DATASET
# ==========================================
# CONFIGURATION
# ==========================================
CROP_DATA_PATH = RAW_CROP_DATA
WEATHER_DIR = WEATHER_DATA_DIR
OUTPUT_PATH = MASTER_DATASET

def load_gov_data():
    print("[INFO] Loading Government Crop Data...")
    if not os.path.exists(CROP_DATA_PATH): return None

    try:
        # 1. Load Data
        dfs = pd.read_html(CROP_DATA_PATH)
        df = dfs[0]
        
        # 2.  Rename Columns by Index
        new_columns = list(df.columns)
        new_columns[0] = 'State'
        new_columns[1] = 'District'
        new_columns[2] = 'Year'
        df.columns = new_columns
        
        # 3. Clean Names (Remove "1. ")
        df['State'] = df['State'].astype(str).str.strip().str.replace(r'^\d+\.\s*', '', regex=True)
        df['District'] = df['District'].astype(str).str.strip().str.replace(r'^\d+\.\s*', '', regex=True)
        
        # 4. Clean Year (Extract 2015 from "2015-16")
        df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})').astype(float).astype(int)
        
        print(f"[SUCCESS] Data loaded. Shape: {df.shape}")
        return df
        
    except Exception as e:
        print(f"[ERROR] Data load failed: {e}")
        return None

def get_annual_weather(district, state, year, cache={}):
    # Filename
    safe_name = f"{district}_{state}".replace(" ", "_").lower()
    file_path = os.path.join(WEATHER_DIR, f"{safe_name}.csv")
    
    if not os.path.exists(file_path):
        return None, None, None

    # Cache optimization
    if file_path not in cache:
        try:
            df = pd.read_csv(file_path)
            
        
            # Convert integer 20150101 -> String "20150101" -> Datetime
            df['Date'] = pd.to_datetime(df.iloc[:, 0].astype(str), format='%Y%m%d')
            
            cache[file_path] = df
        except:
            cache[file_path] = None
            return None, None, None
    
    df = cache[file_path]
    if df is None: return None, None, None

    # Filter for Year
    mask = (df['Date'].dt.year == int(year))
    yearly_data = df.loc[mask]
    
    if yearly_data.empty:
        return None, None, None

    # Calculate Metrics
    return yearly_data['T2M'].mean(), yearly_data['Rain'].sum(), yearly_data['Humidity'].mean()

def merge_data():
    # 1. Load Data
    crop_df = load_gov_data()
    if crop_df is None: return

    # 2. Melt (Wide -> Long)
    print("[INFO] Melting dataset...")
    id_vars = ['State', 'District', 'Year']
    value_vars = [c for c in crop_df.columns if c not in id_vars]
    
    melted_df = pd.melt(crop_df, id_vars=id_vars, value_vars=value_vars, 
                        var_name='Crop_Info', value_name='Value')
    
    # 3. Parse Crop Details
    print("[INFO] Parsing crop details...")
    def parse_crop_info(val, index):
        s = str(val)
        if "'" in s:
            parts = s.split("'")
            if len(parts) > index: return parts[index]
        return "Unknown"

    melted_df['Crop'] = melted_df['Crop_Info'].apply(lambda x: parse_crop_info(x, 1))
    melted_df['Season'] = melted_df['Crop_Info'].apply(lambda x: parse_crop_info(x, 3))
    melted_df['Metric'] = melted_df['Crop_Info'].apply(lambda x: parse_crop_info(x, -2))
    
    # 4. Pivot
    print("[INFO] Pivoting...")
    base_df = melted_df.pivot_table(index=['State', 'District', 'Year', 'Crop', 'Season'], 
                                    columns='Metric', values='Value', aggfunc='first').reset_index()
    base_df.columns.name = None
    
    # 5. Merge Weather
    print(f"[INFO] Merging Weather Data for {len(base_df)} rows...")
    temps, rains, humids = [], [], []
    
    # Use tqdm to show progress
    for index, row in tqdm(base_df.iterrows(), total=len(base_df)):
        t, r, h = get_annual_weather(row['District'], row['State'], row['Year'])
        temps.append(t)
        rains.append(r)
        humids.append(h)
        
    base_df['Avg_Temp'] = temps
    base_df['Total_Rainfall'] = rains
    base_df['Avg_Humidity'] = humids
    
    # 6. Save
    final_df = base_df.dropna(subset=['Avg_Temp'])
    
    print("-" * 30)
    print("MERGE COMPLETE")
    print(f"Original Crop Rows: {len(crop_df)}")
    print(f"Final Dataset Rows: {len(final_df)}")
    print("-" * 30)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    final_df.to_csv(OUTPUT_PATH, index=False)
    print(f"File saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    merge_data()