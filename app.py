from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
import os
import requests
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk

# Download NLTK data
nltk.download('punkt', quiet=True)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache directory
CACHE_DIR = "quran_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Function to fetch full Quran data with both English and Urdu translations
def clean_html_tags(text):
    """Remove HTML tags from text"""
    # First, remove all <sup> tags and their content
    text = re.sub(r'<sup[^>]*>.*?</sup>', '', text)
    # Then remove any other HTML tags but keep their content
    text = re.sub(r'<[^>]*>', '', text)
    return text

def fetch_quran_data():
    base_url = "https://api.quran.com/api/v4/"
    
    # Cache paths
    verses_cache = os.path.join(CACHE_DIR, "verses.json")
    eng_translations_cache = os.path.join(CACHE_DIR, "eng_translations.json")
    urdu_translations_cache = os.path.join(CACHE_DIR, "urdu_translations.json")
    
    # Check if cache exists
    cache_exists = all(os.path.exists(f) for f in [verses_cache, eng_translations_cache, urdu_translations_cache])
    
    if cache_exists:
        try:
            app.logger.info("Loading Quran data from cache...")
            with open(verses_cache, 'r', encoding='utf-8') as f:
                verses = json.load(f)
            with open(eng_translations_cache, 'r', encoding='utf-8') as f:
                eng_translations = json.load(f)
            with open(urdu_translations_cache, 'r', encoding='utf-8') as f:
                urdu_translations = json.load(f)
        except Exception as e:
            app.logger.error(f"Error loading from cache: {e}. Fetching from API...")
            cache_exists = False
    
    if not cache_exists:
        app.logger.info("Fetching Quran data from API (this may take a moment)...")
        
        # Fetch verses
        verses_response = requests.get(base_url + "quran/verses/uthmani")
        verses = verses_response.json()["verses"]
        
        # Fetch English translation (Saheeh International)
        eng_translations_response = requests.get(base_url + "quran/translations/131")
        eng_translations = eng_translations_response.json()["translations"]
        
        # Fetch Urdu translation (Ahmed Ali)
        urdu_translations_response = requests.get(base_url + "quran/translations/54")
        urdu_translations = urdu_translations_response.json()["translations"]
        
        # Cache the data
        with open(verses_cache, 'w', encoding='utf-8') as f:
            json.dump(verses, f, ensure_ascii=False)
        with open(eng_translations_cache, 'w', encoding='utf-8') as f:
            json.dump(eng_translations, f, ensure_ascii=False)
        with open(urdu_translations_cache, 'w', encoding='utf-8') as f:
            json.dump(urdu_translations, f, ensure_ascii=False)
    
    quran_data = {}
    for index, verse in enumerate(verses):
        verse_key = verse["verse_key"]
        
        # Get translations using index
        eng_translation = eng_translations[index]["text"] if index < len(eng_translations) else "English translation not available"
        urdu_translation = urdu_translations[index]["text"] if index < len(urdu_translations) else "Urdu translation not available"
        
        # Clean HTML tags from translations
        eng_translation = clean_html_tags(eng_translation)
        urdu_translation = clean_html_tags(urdu_translation)
        
        quran_data[verse_key] = {
            "arabic": verse["text_uthmani"],
            "eng_translation": eng_translation,
            "urdu_translation": urdu_translation,
        }
    
    return quran_data

# Global variable for storing the Quran data
QURAN_DATA = None
BM25_INDEX = None
VERSE_KEYS = None

def load_quran_data():
    global QURAN_DATA, BM25_INDEX, VERSE_KEYS
    QURAN_DATA = fetch_quran_data()
    
    # Prepare search index
    documents = [QURAN_DATA[key]["eng_translation"] for key in QURAN_DATA]
    tokenized_docs = [word_tokenize(doc.lower()) for doc in documents]
    BM25_INDEX = BM25Okapi(tokenized_docs)
    VERSE_KEYS = list(QURAN_DATA.keys())

# Load data when the server starts
load_quran_data()

# Function to search relevant verses
def search_quran(query, top_n=3):
    tokenized_query = word_tokenize(query.lower())
    scores = BM25_INDEX.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
    
    results = []
    for i in top_indices:
        verse_key = VERSE_KEYS[i]
        results.append({
            "verse_key": verse_key,
            "arabic": QURAN_DATA[verse_key]["arabic"],
            "eng_translation": QURAN_DATA[verse_key]["eng_translation"],
            "urdu_translation": QURAN_DATA[verse_key]["urdu_translation"],
        })
    return results

# Function to get verse by reference
def get_verse_by_reference(verse_ref):
    # Handle various formats like "2:255", "Surah 2 verse 255", etc.
    match = re.search(r'(\d+)[:\s]*(\d+)', verse_ref)
    if match:
        surah = match.group(1)
        verse = match.group(2)
        verse_key = f"{surah}:{verse}"
        
        if verse_key in QURAN_DATA:
            return {
                "verse_key": verse_key,
                "arabic": QURAN_DATA[verse_key]["arabic"],
                "eng_translation": QURAN_DATA[verse_key]["eng_translation"],
                "urdu_translation": QURAN_DATA[verse_key]["urdu_translation"],
            }
    return None

# Function to generate tafseer using Gemini API
def generate_tafseer(verse_key, verse_text, language, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt = ""
    if language.lower() == "english":
        prompt = (
            f"Generate a comprehensive tafseer (explanation) in English for Quran verse {verse_key}.\n\n"
            f"The verse is: \"{verse_text}\"\n\n"
            f"Provide a detailed explanation that includes:\n"
            f"1. Context and background\n"
            f"2. Main message and teachings\n"
            f"3. Scholarly interpretations\n"
            f"4. Practical application\n\n"
            f"Format the response as a cohesive explanation without numbered sections."
        )
    elif language.lower() == "urdu":
        prompt = (
            f"قرآن کی آیت {verse_key} کی اردو میں تفسیر لکھیں۔\n\n"
            f"آیت یہ ہے: \"{verse_text}\"\n\n"
            f"براہ کرم مکمل تفسیر فراہم کریں جس میں شامل ہو:\n"
            f"1. سیاق و سباق اور پس منظر\n"
            f"2. بنیادی پیغام اور تعلیمات\n"
            f"3. علماء کی تشریحات\n"
            f"4. عملی اطلاق\n\n"
            f"اپنا جواب ایک مربوط تشریح کے طور پر دیں، نمبر شدہ حصوں کے بغیر۔"
        )
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        tafseer = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        return tafseer
    except Exception as e:
        app.logger.error(f"Error generating tafseer: {str(e)}")
        return f"Error generating tafseer: {str(e)}"

# Function to generate problem-verse pair using Gemini API
def generate_verse_suggestion(problem_description, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # Modified prompt to request only the verse reference
    prompt = (
        f"Find the most relevant Quranic verse reference (chapter:verse format) for this problem or situation: {problem_description}\n\n"
        f"Respond ONLY with the verse reference in the format chapter:verse (e.g., 2:255 or 24:35). "
        f"Do not include the actual text of the verse or any other information."
    )
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        verse_ref = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        
        # Extract just the verse reference
        match = re.search(r'(\d+)[:\s]*(\d+)', verse_ref)
        if match:
            surah = match.group(1)
            verse = match.group(2)
            verse_ref = f"{surah}:{verse}"
        
        # Look up the verse in our dataset
        verse_data = get_verse_by_reference(verse_ref)
        if verse_data:
            # Generate English tafseer
            app.logger.info("Generating English tafseer...")
            eng_tafseer = generate_tafseer(
                verse_data["verse_key"], 
                verse_data["eng_translation"],
                "english",
                api_key
            )
            
            # Generate Urdu tafseer
            app.logger.info("Generating Urdu tafseer...")
            urdu_tafseer = generate_tafseer(
                verse_data["verse_key"], 
                verse_data["urdu_translation"],
                "urdu",
                api_key
            )
            
            # Add tafseer to the verse data
            verse_data["eng_tafseer"] = eng_tafseer
            verse_data["urdu_tafseer"] = urdu_tafseer
            
            return verse_data
        else:
            return {"error": f"Verse reference {verse_ref} not found in the Quran dataset."}
            
    except Exception as e:
        app.logger.error(f"Error getting AI suggestion: {str(e)}")
        return {"error": f"Error getting AI suggestion: {str(e)}"}

# API Routes
@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    num_results = data.get('numResults', 3)
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        results = search_quran(query, top_n=num_results)
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Error searching Quran: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/verse/<reference>', methods=['GET'])
def get_verse(reference):
    try:
        verse = get_verse_by_reference(reference)
        if verse:
            return jsonify(verse)
        else:
            return jsonify({"error": "Verse not found"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching verse: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/suggest', methods=['POST'])
def suggest():
    data = request.json
    problem = data.get('problem')
    api_key = data.get('apiKey')
    
    if not problem:
        return jsonify({"error": "No problem description provided"}), 400
    
    if not api_key:
        return jsonify({"error": "No API key provided"}), 400
    
    try:
        result = generate_verse_suggestion(problem, api_key)
        if "error" in result:
            return jsonify({"error": result["error"]}), 400
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error getting suggestion: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tafseer', methods=['POST'])
def tafseer():
    data = request.json
    verse_key = data.get('verseKey')
    translation = data.get('translation')
    language = data.get('language')
    api_key = data.get('apiKey')
    
    if not all([verse_key, translation, language, api_key]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        tafseer_text = generate_tafseer(verse_key, translation, language, api_key)
        return jsonify({"tafseer": tafseer_text})
    except Exception as e:
        app.logger.error(f"Error generating tafseer: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Serve React frontend from the static folder
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join('build', path)):
        return send_from_directory('build', path) # type: ignore
    return send_from_directory('build', 'index.html') # type: ignore

if __name__ == '__main__':
    app.run(debug=True, port=5000)