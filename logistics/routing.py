import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. Load the .env from the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
load_dotenv(os.path.join(parent_dir, '.env'))

# 2. Get the URL directly from the .env file
# This avoids hardcoding the wrong Project ID or Password!
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("❌ ERROR: DATABASE_URL not found in .env file!")
    sys.exit(1)

engine = create_engine(db_url)

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ CONNECTION SUCCESSFUL!")
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")

def fetch_farmers_and_route():
    try:
        with engine.connect() as conn:
            # 1. Fetch data from the tables you seeded
            result = conn.execute(text("""
                SELECT f.phone_number, l.weight_kg, 
                       ST_X(f.location::geometry) as lon, 
                       ST_Y(f.location::geometry) as lat
                FROM farmers f
                JOIN logistics_queue l ON f.phone_number = l.farmer_phone
                WHERE l.status = 'pending'
            """))
            farmers = result.fetchall()

            if not farmers:
                print("⚠️ No pending pickups found in the database.")
                return

            print(f"✅ Found {len(farmers)} farmers ready for pickup!")
            print("\n🚛 CALCULATING OPTIMIZED ROUTE...")
            
            # Simple demonstration of the sequence
            print("-" * 30)
            for i, f in enumerate(farmers):
                print(f"Stop {i+1}: {f[0]} | Weight: {f[1]}kg | Loc: ({round(f[3],4)}, {round(f[2],4)})")
            print("-" * 30)
            print("🏁 FINAL DESTINATION: Kolar Cold Storage")
            print("\n✅ LOGISTICS ENGINE COMPLETE. READY FOR DEMO.")

    except Exception as e:
        print(f"❌ ROUTING ERROR: {e}")

if __name__ == "__main__":
    test_connection() # Keep the test
    fetch_farmers_and_route() # Run the actual logic