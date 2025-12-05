import os

# Base Directory (Root of the project)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory Structure
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
INTERIM_DIR = os.path.join(DATA_DIR, "interim")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODEL_READY_DIR = os.path.join(PROCESSED_DIR, "model_ready")

# File Paths
RAW_CROP_DATA = os.path.join(RAW_DIR, "gov_crop_data", "crop_production_2015_2023.xls")
DISTRICT_MAPPING = os.path.join(INTERIM_DIR, "district_mapping.csv")
WEATHER_DATA_DIR = os.path.join(RAW_DIR, "nasa_weather")
MASTER_DATASET = os.path.join(PROCESSED_DIR, "KrishiSense_Master_Dataset.csv")

# Analysis Configuration
SEASON_START_MONTH = 1
SEASON_END_MONTH = 12

# Target Crops for Modeling (The Risk Trinity)
TARGET_CROPS = {
    'Sugarcane': 'cash_crop',
    'Onion': 'horticulture',
    'Potato': 'horticulture',
    'Turmeric': 'spice',
    'Ginger': 'spice',
    'Dry chillies': 'spice',
    'Garlic': 'spice'
}