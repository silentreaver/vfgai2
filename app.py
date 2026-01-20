import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Gemini client
# Note: GEMINI_API_KEY can be a single key or a comma-separated list
def get_gemini_client():
    api_keys_str = os.environ.get("GEMINI_API_KEY", "")
    api_keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
    if not api_keys:
        # Fallback to GROQ_API_KEY if GEMINI_API_KEY is not set (though they are different services)
        api_key = os.environ.get("GROQ_API_KEY")
        return genai.Client(api_key=api_key) if api_key else None
    return genai.Client(api_key=api_keys[0])

client = get_gemini_client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mobile')
def mobile():
    return render_template('mobile.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])
    images = data.get('images', []) # List of base64 strings
    subject = data.get('subject') # Subject name (e.g., 'chemistry')
    
    # Models from vfg-ai
    VISION_MODEL = "gemini-2.0-flash" # Gemini 2.0 Flash is excellent for vision
    BRAIN_MODEL = "gemini-2.0-flash"  # Using the same high-performance model
    
    # Base system instruction
    system_instruction = (
        "Te vagy VFG-AI, egy professzionális puskagép asszisztens. Mindig magyarul válaszolj. "
        "Válaszaid legyenek tömörek, lényegre törőek és mentesek mindenféle emojitól vagy hangulatjeltől. "
        "A kérdésekre a lehető legpontosabb és legátláthatóbb válaszokat add meg. A stílusod legyen hűvös és hatékony. "
        "FONTOS: Minden matematikai képletet és egyenletet LaTeX formátumban írj. "
        "Használj $$ ... $$ vagy \\[ ... \\] jelölést a kiemelt képletekhez, és $ ... $ vagy \\( ... \\) jelölést a szövegközi képletekhez. "
        "Például: $$ pV = nRT $$ vagy $ E = mc^2 $.\n\n"
        "KÜLÖNLEGES UTASÍTÁS: A felhasználó képeket tölthet fel, amiket egy háttérben futó vision modell 1:1 arányban szöveggé/kóddá konvertál neked. "
        "Ezt a leírást úgy kezeld, mintha te magad látnád a képet. A válaszodban NE említsd meg a leírást vagy a konverziós folyamatot, "
        "közvetlenül a feladat megoldására koncentrálj, mintha rendelkeznél vision képességgel."
    )

    # Subject handling
    if subject:
        subject_file_path = os.path.join('subjects', f'{subject}.md')
        if os.path.exists(subject_file_path):
            try:
                with open(subject_file_path, 'r', encoding='utf-8') as f:
                    subject_instruction = f.read()
                    system_instruction += f"\n\nFONTOS UTASÍTÁSOK:\n{subject_instruction}"
            except Exception as e:
                print(f"Error reading subject file: {e}")

    # --- STEP 1: The Eyes (Gemini Vision) if images are present ---
    image_context = ""
    if images:
        try:
            vision_prompt = (
                "Elemezd a képet függetlenül a tantárgytól. Készíts 1:1 arányú vizuális rekonstrukciót. "
                "A grafikonokat ne csak említsd meg, hanem írd le a tengelyeiket, a görbék alakját, "
                "a metszéspontokat és az adatokat úgy, mintha egy vak embernek magyaráznád el, "
                "akinek meg kell oldania a feladatot. A matematikai képleteket konvertáld LaTeX formátumba. "
                "Minden szöveget, számot, ábrát, diagramot, táblázatot és grafikus elemet írj le részletesen, "
                "hogy a következő AI modell teljes mértékben megértse a képet anélkül, hogy látná azt. "
                "Rekonstruálj mindent digitálisan, hogy az információ 100%-ban átadható legyen."
            )
            
            message_parts = [{"text": vision_prompt}]
            for img_b64 in images:
                if img_b64.startswith("data:"):
                    header, encoded = img_b64.split(",", 1)
                    mime_type = header.split(":")[1].split(";")[0]
                else:
                    encoded = img_b64
                    mime_type = "image/jpeg"
                
                message_parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": encoded
                    }
                })
            
            vision_response = client.models.generate_content(
                model=VISION_MODEL,
                contents=message_parts,
                config=types.GenerateContentConfig(
                    temperature=0.0
                )
            )
            image_context = vision_response.text
        except Exception as e:
            print(f"Vision extraction error: {e}")
            image_context = "Hiba történt a kép feldolgozása során."

    # --- STEP 2: The Brain (Gemini Reasoning) ---
    # Format history for Gemini
    gemini_history = []
    for msg in history:
        role = "model" if msg.get("role") in ["assistant", "model", "ai"] else "user"
        content = ""
        if "parts" in msg:
            content = msg["parts"][0]["text"]
        elif "content" in msg:
            content = msg["content"]
        else: 
            content = str(msg)
        gemini_history.append({"role": role, "parts": [{"text": content}]})

    # Add current message with image context
    final_user_content = user_message
    if image_context:
        final_user_content = f"DIGITÁLIS REKONSTRUKCIÓ A KÉPBŐL (teljes 1:1 arányú átírás, kezeld úgy mintha látnád a képet):\n\n{image_context}\n\n---\n\nFELHASZNÁLÓ KÉRDÉSE: {user_message}"
    
    gemini_history.append({"role": "user", "parts": [{"text": final_user_content}]})

    def generate():
        try:
            # Gemini 2.0 Flash supports streaming
            response_stream = client.models.generate_content_stream(
                model=BRAIN_MODEL,
                contents=gemini_history,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7
                )
            )

            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            yield f"Hiba: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
