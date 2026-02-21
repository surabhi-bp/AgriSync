import os
import sys
import random
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. Get the path to the AgriSync-1 folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# 2. Specifically load the .env file from the parent folder
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)

# 3. Fetch the URL
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print(f"❌ Error: DATABASE_URL not found. Path searched: {dotenv_path}")
    sys.exit(1)

engine = create_engine(db_url)

def seed_farmers():
    # Central point: Kolar, Karnataka
    KOLAR_LAT, KOLAR_LON = 13.137, 78.129
    CROPS = ["Tomato", "Onion", "Potato", "Chilli"]
    
    print("🌱 Starting to seed the Demo Universe...")
    
    with engine.connect() as conn:
        for i in range(20):
            # Generate a random phone number
            phone = f"+919845{random.randint(10000, 99999)}"
            
            # Create a GPS point within ~10km of Kolar
            lat = KOLAR_LAT + random.uniform(-0.07, 0.07)
            lon = KOLAR_LON + random.uniform(-0.07, 0.07)
            
            # 1. Insert into Farmers table (Using PostGIS logic)
            conn.execute(text("""
                INSERT INTO farmers (phone_number, location, pref_lang)
                VALUES (:phone, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 'kannada')
                ON CONFLICT (phone_number) DO NOTHING;
            """), {"phone": phone, "lat": lat, "lon": lon})

            # 2. Insert into Logistics Queue (Current harvest requests)
            conn.execute(text("""
                INSERT INTO logistics_queue (farmer_phone, crop_type, weight_kg)
                VALUES (:phone, :crop, :weight);
            """), {
                "phone": phone, 
                "crop": random.choice(CROPS), 
                "weight": random.randint(30, 450)
            })
        
        conn.commit()
    print("✅ Successfully added 20 fake farmers and harvest requests to Supabase!")

if __name__ == "__main__":
    seed_farmers()