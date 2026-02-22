import os
import google.generativeai as genai
import json
import re
from dotenv import load_dotenv

load_dotenv()

# 1. SETUP
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# UPDATE: As of Feb 2026, 'gemini-1.5' models are often legacy. 
# 'gemini-2.5-flash' is the stable current standard for the Free Tier.
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception:
    # Fallback to the latest preview if stable isn't hit
    model = genai.GenerativeModel('gemini-3.1-pro-preview')

def process_farmer_message(incoming_text):
    """
    Uses Gemini AI to detect language, translate, and extract intent.
    """
    prompt = f"""
    Analyze this message from a farmer: "{incoming_text}"
    
    1. Detect the language code (e.g., 'hi', 'kn', 'en').
    2. Identify the intent: 'price_check', 'logistics', or 'general'.
    3. Identify the crop (e.g., 'tomato').
    4. Identify weight in KG (number only).

    Return ONLY a raw JSON object:
    {{
        "detected_lang": "hi",
        "intent": "general",
        "crop": "tomato",
        "weight_kg": null
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Use regex to find the JSON block in case of extra text
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            raise ValueError("No JSON block found in response")

    except Exception as e:
        print(f"❌ AI Error in Detection: {e}")
        return {"detected_lang": "en", "intent": "general", "crop": "tomato", "weight_kg": None}

def translate_reply_to_farmer(english_text, target_lang):
    """
    Translates the final reply back to the farmer's language.
    """
    if not target_lang or target_lang == 'en':
        return english_text
        
    try:
        prompt = f"Translate the following text into language code '{target_lang}'. Provide ONLY the translated text: {english_text}"
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ Translation Error: {e}")
        return english_text