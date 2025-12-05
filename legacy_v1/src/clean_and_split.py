import pandas as pd
import os
import numpy as np
from src.config import MASTER_DATASET, MODEL_READY_DIR, TARGET_CROPS

def clean_and_split():
    print("[INFO] Starting Preprocessing Pipeline...")
    
    if not os.path.exists(MASTER_DATASET):
        print(f"[ERROR] Master dataset not found at {MASTER_DATASET}")
        return

    # 1. Load Master Dataset
    df = pd.read_csv(MASTER_DATASET)
    print(f"Original Rows: {len(df)}")

    # 2. Filter for Target Crops
    # We only keep the crops defined in config.py
    df = df[df['Crop'].isin(TARGET_CROPS.keys())].copy()
    print(f"Filtered Rows (Target Crops): {len(df)}")

    # 3. Impute Missing Yields
    # Strategy: Use District Average first. If missing, use State Average.
    print("[INFO] Imputing missing values...")
    
    # Group by District+Crop and fill NaNs with the mean
    df['Yield (Tonne/Hectare)'] = df.groupby(['District', 'Crop'])['Yield (Tonne/Hectare)'].transform(
        lambda x: x.fillna(x.mean())
    )
    
    # Fallback: Group by State+Crop and fill NaNs
    df['Yield (Tonne/Hectare)'] = df.groupby(['State', 'Crop'])['Yield (Tonne/Hectare)'].transform(
        lambda x: x.fillna(x.mean())
    )
    
    # Drop rows that are still missing critical data (likely no weather data found)
    df = df.dropna(subset=['Yield (Tonne/Hectare)', 'Avg_Temp', 'Total_Rainfall'])

    # 4. Feature Engineering (Adding Intelligence)
    print("[INFO] Engineering Features...")
    
    # A. Temp Stress: Deviation from optimal growing temp (approx 25 C)
    df['Temp_Stress'] = abs(df['Avg_Temp'] - 25.0)
    
    # B. Rainfall Deviation: Difference between this year's rain and the district's long-term average
    district_rain_mean = df.groupby('District')['Total_Rainfall'].transform('mean')
    df['Rain_Deviation'] = df['Total_Rainfall'] - district_rain_mean
    
    # C. Yield Class: Binary Classification for SVM (1 = High Yield, 0 = Low Yield)
    # Calculated based on whether the yield is above or below the crop's global average
    crop_mean_yield = df.groupby('Crop')['Yield (Tonne/Hectare)'].transform('mean')
    df['Yield_Class'] = (df['Yield (Tonne/Hectare)'] > crop_mean_yield).astype(int)

    # 5. Split and Save specific datasets
    os.makedirs(MODEL_READY_DIR, exist_ok=True)
    
    # Dataset A: Sugarcane (For Regression, Clustering, SVM)
    sugar_df = df[df['Crop'] == 'Sugarcane']
    sugar_path = os.path.join(MODEL_READY_DIR, "sugarcane_modeling.csv")
    sugar_df.to_csv(sugar_path, index=False)
    print(f"Saved Sugarcane Data: {len(sugar_df)} rows")
    
    # Dataset B: Spices (For Association Rules)
    # Extract keys from config where value is 'spice'
    spices = [k for k, v in TARGET_CROPS.items() if v == 'spice']
    spice_df = df[df['Crop'].isin(spices)]
    spice_path = os.path.join(MODEL_READY_DIR, "spices_modeling.csv")
    spice_df.to_csv(spice_path, index=False)
    print(f"Saved Spices Data: {len(spice_df)} rows")
    
    # Dataset C: Horticulture (For Price Prediction reference/future use)
    veg_df = df[df['Crop'].isin(['Onion', 'Potato'])]
    veg_path = os.path.join(MODEL_READY_DIR, "horticulture_modeling.csv")
    veg_df.to_csv(veg_path, index=False)
    print(f"Saved Horticulture Data: {len(veg_df)} rows")

    print(f"\n[SUCCESS] Datasets saved to {MODEL_READY_DIR}")

if __name__ == "__main__":
    clean_and_split()