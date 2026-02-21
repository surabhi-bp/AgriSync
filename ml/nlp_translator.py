from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

# ==========================================
# 1. FALLBACK DICTIONARY 
# ==========================================
KANNADA_FALLBACK = {
    "ಬೆಲೆ": "price",
    "ಮಳೆ": "rain",
    "ಟೊಮೆಟೊ": "tomato",
    "ಈರುಳ್ಳಿ": "onion",
    "ಸಹಾಯ": "help",
    "ನಮಸ್ಕಾರ": "hello"
}

# ==========================================
# 2. NLP TRANSLATION LAYER
# ==========================================
def translate_to_english(incoming_text):
    """
    Detects the language and translates to English. 
    Uses fallback dictionary if APIs fail.
    """
    try:
        # 1. Detect the language
        detected_lang = detect(incoming_text)
        
        # 2. If it's already English, just return it
        if detected_lang == 'en':
            return incoming_text.lower(), 'en'
            
        # 3. Translate to English
        translated_text = GoogleTranslator(source='auto', target='en').translate(incoming_text)
        return translated_text.lower(), detected_lang
        
    except LangDetectException:
        print("Could not detect language.")
        return incoming_text.lower(), 'en'
        
    except Exception as e:
        print(f"API Failed. Checking fallback dictionary... Error: {e}")
        for kannada_word, english_word in KANNADA_FALLBACK.items():
            if kannada_word in incoming_text:
                return english_word, 'kn'
        return incoming_text.lower(), 'en'

def translate_from_english(english_text, target_lang):
    """
    Translates the bot's English response back to the farmer's language.
    """
    if target_lang == 'en':
        return english_text
    try:
        translated_text = GoogleTranslator(source='en', target=target_lang).translate(english_text)
        return translated_text
    except Exception:
        return english_text

# ==========================================
# 3. SPATIAL DATA INGESTION
# ==========================================
def parse_gps_coordinates(whatsapp_location_string):
    """
    Takes a messy WhatsApp location string and returns clean floats.
    """
    try:
        lat_str, lon_str = whatsapp_location_string.split(',')
        return float(lat_str.strip()), float(lon_str.strip())
    except ValueError:
        print("Error: Could not parse GPS string.")
        return None, None

# --- QUICK TEST TO VERIFY YOUR WORK ---
if __name__ == "__main__":
    print("--- Testing NLP Translation ---")
    test_text = "ನಮಸ್ಕಾರ, ನನಗೆ ಟೊಮೆಟೊ ಬೆಲೆ ಬೇಕು" # "Hello, I want tomato price"
    eng_text, lang = translate_to_english(test_text)
    print(f"Farmer sent: {test_text}")
    print(f"Bot understood: {eng_text} | Detected Language: {lang}")
    
    bot_reply = "The price of tomatoes is 22 rupees."
    local_reply = translate_from_english(bot_reply, lang)
    print(f"Bot replies to farmer: {local_reply}")
    
    print("\n--- Testing Spatial Parser ---")
    raw_gps = "13.0123, 77.5432"
    lat, lon = parse_gps_coordinates(raw_gps)
    print(f"Raw String: {raw_gps} | Cleaned Lat: {lat}, Cleaned Lon: {lon}")