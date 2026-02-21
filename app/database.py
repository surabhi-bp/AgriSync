import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Search for .env in the current directory or parent directory
load_dotenv() 

db_url = os.getenv("DATABASE_URL")

if db_url is None:
    raise ValueError("❌ ERROR: DATABASE_URL not found in .env file. Check your variable names!")

engine = create_engine(db_url)

def save_farmer_to_db(phone, lat, lon, lang):
    """Saves or updates farmer location using PostGIS spatial points"""
    query = text("""
        INSERT INTO farmers (phone_number, location, pref_lang)
        VALUES (:phone, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), :lang)
        ON CONFLICT (phone_number) DO UPDATE SET location = EXCLUDED.location;
    """)
    with engine.connect() as conn:
        conn.execute(query, {"phone": phone, "lat": lat, "lon": lon, "lang": lang})
        conn.commit()

def add_to_logistics_queue(phone, crop, weight):
    """Adds a transport request to the queue"""
    query = text("""
        INSERT INTO logistics_queue (farmer_phone, crop_type, weight_kg, pickup_date)
        VALUES (:phone, :crop, :weight, CURRENT_DATE);
    """)
    with engine.connect() as conn:
        conn.execute(query, {"phone": phone, "crop": crop, "weight": weight})
        conn.commit()