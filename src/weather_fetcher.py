import pandas as pd
import requests
import os
import time
from tqdm import tqdm

INPUT_COORDS = os.path.join("data", "interim", "district_mapping.csv")
OUTPUT_FOLDER = os.path.join("data", "raw", "nasa_weather")
BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

def fetch_weather():
    if not os.path.exists(INPUT_COORDS): return
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    districts = pd.read_csv(INPUT_COORDS).dropna(subset=['latitude', 'longitude'])

    print(f"Fetching weather for {len(districts)} locations...")

    for idx, row in tqdm(districts.iterrows(), total=len(districts)):
        safe_name = f"{row['district_name']}_{row['state_name']}".replace(" ", "_").lower()
        fname = os.path.join(OUTPUT_FOLDER, f"{safe_name}.csv")

        if os.path.exists(fname): continue

        params = {
            "parameters": "T2M,PRECTOTCORR,RH2M",
            "community": "AG",
            "longitude": row['longitude'],
            "latitude": row['latitude'],
            "start": "20150101", "end": "20231231",
            "format": "JSON"
        }

        try:
            response = requests.get(BASE_URL, params=params)
            if response.status_code == 200:
                data = response.json()['properties']['parameter']
                df = pd.DataFrame({
                    'T2M': data['T2M'],
                    'Rain': data['PRECTOTCORR'],
                    'Humidity': data['RH2M']
                })
                df.to_csv(fname)
        except Exception as e:
            print(f"Error {row['district_name']}: {e}")

        time.sleep(1.2) # Rate limit

if __name__ == "__main__":
    fetch_weather()