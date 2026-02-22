# App/ml/geocoder.py
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# Initialize the OpenStreetMap API
# REQUIRED: You must use a unique user_agent so OpenStreetMap doesn't block you
geolocator = Nominatim(user_agent="agrisync_production_bot_v1")

def get_district_from_coords(lat, lon, retries=2):
    """
    Takes a latitude and longitude and returns the District name in UPPERCASE.
    Includes retry logic in case the OpenStreetMap server is slow.
    """
    # Fallback/Safety Check
    if not lat or not lon:
        return "UNKNOWN"

    for attempt in range(retries):
        try:
            # exactly_one=True returns the single best match
            # timeout=5 ensures your FastAPI server doesn't freeze if the map server is down
            location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True, timeout=5)
            
            if location and 'address' in location.raw:
                address = location.raw['address']
                
                # OpenStreetMap stores Indian districts usually under 'state_district'
                # If not found, fallback to 'county', then fallback to 'Unknown'
                district = address.get('state_district', address.get('county', 'Unknown'))
                
                # Clean the string so it matches your Agmarknet CSV exactly
                # Example: "Kolar District" becomes "KOLAR"
                clean_district = district.replace(" District", "").replace(" district", "").strip().upper()
                
                return clean_district
                
            return "UNKNOWN"
            
        except GeocoderTimedOut:
            print(f"⚠️ Geocoder timed out. Retrying {attempt + 1}/{retries}...")
            time.sleep(1) # Wait 1 second before trying again
            
        except GeocoderServiceError as e:
            print(f"❌ Geocoder API Error: {e}")
            return "UNKNOWN"
            
        except Exception as e:
            print(f"❌ Unexpected Geocoding Error: {e}")
            return "UNKNOWN"

    # If all retries fail
    return "UNKNOWN"