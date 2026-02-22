from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import uvicorn
import re

# ML Translation, Prediction, and Location layers
from app.ml.nlp_translator import process_farmer_message, translate_reply_to_farmer
from app.ml.crop_predictor import get_real_price
from app.ml.geocoder import get_district_from_coords  

# Database functions
from .database import get_farmer, save_farmer_to_db, add_to_logistics_queue, save_farmer_language

app = FastAPI()

def detect_script_manually(text):
    """Backup check: If message contains Hindi or Kannada characters, return the code."""
    if re.search(r'[\u0900-\u097F]', text):  # Hindi/Devanagari range
        return "hi"
    if re.search(r'[\u0C80-\u0CFF]', text):  # Kannada range
        return "kn"
    return None

@app.post("/message")
async def whatsapp_webhook(
    Body: str = Form(""), 
    From: str = Form(...),
    Latitude: float = Form(None),
    Longitude: float = Form(None)
):
    print(f"\n--- NEW INCOMING MESSAGE ---")
    print(f"Sender: {From}")
    
    phone_number = From.replace("whatsapp:", "").strip()
    farmer = get_farmer(phone_number)
    
    # Default values
    target_lang = "en"
    llm_data = {"detected_lang": "en", "intent": "general", "crop": "tomato"}

    # 1. LANGUAGE DETECTION
    if Body and Body.strip():
        # A. Try AI Detection
        llm_data = process_farmer_message(Body)
        target_lang = llm_data.get("detected_lang", "en")
        
        # B. Manual Override (If AI fails but script is clearly Hindi/Kannada)
        manual_lang = detect_script_manually(Body)
        if manual_lang:
            target_lang = manual_lang
            
        print(f"🧠 Detected Language: {target_lang}")
        save_farmer_language(phone_number, target_lang)
    else:
        # Fallback to database if it's just a location pin
        target_lang = farmer.get("lang", "en") if farmer else "en"

    english_reply = ""

    # 2. BUSINESS LOGIC (Always generates English first)
    if Latitude and Longitude:
        save_farmer_to_db(phone_number, Latitude, Longitude, target_lang)
        district = get_district_from_coords(Latitude, Longitude)
        english_reply = (
            f"Registration successful in {district}!\n\n"
            "I have saved your farm location. How can I help you today?\n"
            "- Ask for prices (e.g., 'Tomato price')\n"
            "- Request a truck (e.g., 'I need a truck for 500kg onions')"
        )

    elif not farmer or farmer.get('lat') is None:
        english_reply = (
            "Welcome to AgriSync! Please send your WhatsApp location pin 📎 "
            "so we can register your farm and provide local prices."
        )

    else:
        intent = llm_data.get("intent")
        
        # Simple numeric menu fallback
        if Body.strip() == "1": intent = "price_check"
        elif Body.strip() == "2": intent = "logistics"

        if intent == "price_check":
            crop = llm_data.get("crop") or "tomato"
            district = get_district_from_coords(farmer['lat'], farmer['lon'])
            english_reply = get_real_price(crop, district)
        
        elif intent == "logistics":
            crop = llm_data.get("crop") or "tomato"
            weight = llm_data.get("weight_kg") or 100
            add_to_logistics_queue(phone_number, crop, weight)
            english_reply = f"Request recorded: {weight}kg of {crop}. Our team will contact you soon."
        
        else:
            english_reply = (
                "How can I help you? You can ask for:\n"
                "1. Market Price (e.g., 'Tomato price')\n"
                "2. Schedule Pickup (e.g., 'Send truck for 300kg onions')"
            )

    # 3. THE TRANSLATION STEP (Crucial)
    print(f"🔄 Translating English to {target_lang}...")
    final_reply = translate_reply_to_farmer(english_reply, target_lang)
    
    response = MessagingResponse()
    response.message(final_reply)
    
    print(f"📡 Sending Response: {final_reply[:50]}...")
    return Response(content=str(response), media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)