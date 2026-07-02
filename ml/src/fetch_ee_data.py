"""
fetch_ee_data.py - Fetch real Earth Engine data from command line
Usage: python fetch_ee_data.py --lat 19.99 --lon 73.78 --date 2025-06-15
"""

import ee
import argparse
from datetime import datetime, timedelta

def get_ndvi(lat, lon, date_str, days_window=30):
    """Fetch NDVI for a specific location and date."""
    try:
        ee.Initialize(project='studymate-4fc50')
    except:
        print("❌ Earth Engine not initialized. Run registration first.")
        return None
    
    point = ee.Geometry.Point([lon, lat])
    end_date = datetime.strptime(date_str, '%Y-%m-%d')
    start_date = end_date - timedelta(days=days_window)
    
    print(f"📍 Location: {lat}, {lon}")
    print(f"📅 Date range: {start_date.date()} to {end_date.date()}")
    
    # Get Sentinel-2 imagery
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(point)
        .filterDate(start_date.isoformat(), end_date.isoformat())
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )
    
    size = collection.size().getInfo()
    print(f"📸 Found {size} cloud-free images")
    
    if size == 0:
        print("⚠️  No images found")
        return None
    
    # Compute NDVI
    def add_ndvi(img):
        ndvi = img.normalizedDifference(["B8", "B4"]).rename("ndvi")
        return img.addBands(ndvi)
    
    mean_ndvi = collection.map(add_ndvi).select("ndvi").mean()
    
    # Get NDVI at point
    value = mean_ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=10
    ).get("ndvi").getInfo()
    
    if value is None:
        print("⚠️  No NDVI value at this point")
        return None
    
    return round(float(value), 4)

def get_weather_data(lat, lon, date_str):
    """Fetch weather data from NASA POWER API."""
    import requests
    from datetime import datetime
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    start = date_obj.strftime("%Y%m%d")
    end = (date_obj + timedelta(days=7)).strftime("%Y%m%d")
    
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,WS2M&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
    
    try:
        r = requests.get(url, timeout=30)
        data = r.json()['properties']['parameter']
        
        # Get average values
        temps = list(data['T2M_MAX'].values())
        avg_temp = sum(temps) / len(temps)
        
        print(f"🌡️  Avg Temp: {avg_temp:.1f}°C")
        print(f"💧 Humidity: {list(data['RH2M'].values())[0]:.1f}%")
        print(f"🌧️  Rainfall: {list(data['PRECTOTCORR'].values())[0]:.1f}mm")
        print(f"💨 Wind: {list(data['WS2M'].values())[0]*3.6:.1f}km/h")
        
        return {
            'temp': avg_temp,
            'humidity': list(data['RH2M'].values())[0],
            'rainfall': list(data['PRECTOTCORR'].values())[0],
            'wind': list(data['WS2M'].values())[0] * 3.6
        }
    except Exception as e:
        print(f"⚠️  Weather fetch failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch Earth Engine data')
    parser.add_argument('--lat', type=float, required=True, help='Latitude')
    parser.add_argument('--lon', type=float, required=True, help='Longitude')
    parser.add_argument('--date', type=str, default='2025-06-15', help='Date (YYYY-MM-DD)')
    parser.add_argument('--ndvi', action='store_true', help='Get NDVI only')
    parser.add_argument('--weather', action='store_true', help='Get weather only')
    
    args = parser.parse_args()
    
    print("🌍 Fetching Earth Engine Data")
    print("=" * 50)
    
    if not args.weather:
        ndvi = get_ndvi(args.lat, args.lon, args.date)
        if ndvi is not None:
            print(f"\n✅ NDVI: {ndvi}")
    
    if not args.ndvi:
        weather = get_weather_data(args.lat, args.lon, args.date)