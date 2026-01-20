import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
from groq import Groq
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Clients
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_gemini_client():
    api_keys_str = os.environ.get("GEMINI_API_KEY", "")
    api_keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
    if not api_keys:
        return None
    return genai.Client(api_key=api_keys[0])

gemini_client = get_gemini_client()

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
    images = data.get('images', [])
    subject = data.get('subject')
    selected_model = data.get('model', 'gemini-3-flash-preview') # Default model
    
    # Base system instruction
    system_instruction = (
        "Te vagy VFG-AI, egy professzionális puskagép asszisztens. Mindig magyarul válaszolj. "
        "Válaszaid legyenek tömörek, lényegre törőek és mentesek mindenféle emojitól vagy hangulatjeltől. "
        "A kérdésekre a lehető legpontosabb és legátláthatóbb válaszokat add meg. A stílusod legyen hűvös és hatékony. "
        "FONTOS: Minden matematikai képletet és egyenletet LaTeX formátumban írj. "
        "Használj $$ ... $$ vagy \\[ ... \\] jelölést a kiemelt képletekhez, és $ ... $ vagy \\( ... \\) jelölést a szövegközi képletekhez."
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

    # --- MODEL LOGIC ---
    
    if "gemini" in selected_model:
        # --- GEMINI LOGIC (Native Multimodal) ---
        if not gemini_client:
            return Response("Hiba: GEMINI_API_KEY nincs beállítva.", status=500)
            
        message_parts = []
        for img_b64 in images:
            if img_b64.startswith("data:"):
                header, encoded = img_b64.split(",", 1)
                mime_type = header.split(":")[1].split(";")[0]
            else:
                encoded = img_b64
                mime_type = "image/jpeg"
            message_parts.append({"inline_data": {"mime_type": mime_type, "data": encoded}})
        
        if user_message:
            message_parts.append({"text": user_message})

        gemini_history = []
        for msg in history:
            role = "model" if msg.get("role") in ["assistant", "model", "ai"] else "user"
            content = msg.get("parts", [{}])[0].get("text", "") if "parts" in msg else msg.get("content", "")
            gemini_history.append({"role": role, "parts": [{"text": content}]})

        full_contents = gemini_history + [{"role": "user", "parts": message_parts}]

        def generate_gemini():
            try:
                response_stream = gemini_client.models.generate_content_stream(
                    model=selected_model,
                    contents=full_contents,
                    config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)
                )
                for chunk in response_stream:
                    if chunk.text: yield chunk.text
            except Exception as e: yield f"Hiba: {str(e)}"
        return Response(stream_with_context(generate_gemini()), mimetype='text/plain')

    else:
        # --- GROQ / MAVERICK LOGIC (Vision -> Reasoning Chain) ---
        VISION_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
        BRAIN_MODEL = "groq/compound" if selected_model == "groq-compound" else VISION_MODEL
        
        image_context = ""
        if images:
            try:
                vision_prompt = "Elemezd a képet függetlenül a tantárgytól. Készíts 1:1 arányú vizuális rekonstrukciót. A grafikonokat ne csak említsd meg, hanem írd le a tengelyeiket, a görbék alakját, a metszéspontokat és az adatokat úgy, mintha egy vak embernek magyaráznád el. A matematikai képleteket konvertáld LaTeX formátumba."
                vision_messages = [{"role": "user", "content": [{"type": "text", "text": vision_prompt}]}]
                for img_b64 in images:
                    vision_messages[0]["content"].append({"type": "image_url", "image_url": {"url": img_b64}})
                
                vision_response = groq_client.chat.completions.create(model=VISION_MODEL, messages=vision_messages, temperature=0.0)
                image_context = vision_response.choices[0].message.content
            except Exception as e:
                image_context = f"Hiba a képfeldolgozás során: {e}"

        api_messages = [{"role": "system", "content": system_instruction + "\n\nKÜLÖNLEGES UTASÍTÁS: A kapott képleírást kezeld úgy, mintha látnád a képet. Ne említsd a konverziót."}]
        for msg in history:
            role = "assistant" if msg.get("role") in ["model", "ai", "assistant"] else "user"
            content = msg.get("content", "") or (msg.get("parts", [{}])[0].get("text", "") if "parts" in msg else "")
            api_messages.append({"role": role, "content": content})

        final_user_content = user_message
        if image_context:
            final_user_content = f"DIGITÁLIS REKONSTRUKCIÓ A KÉPBŐL:\n\n{image_context}\n\n---\n\nFELHASZNÁLÓ KÉRDÉSE: {user_message}"
        api_messages.append({"role": "user", "content": final_user_content})

        def generate_groq():
            try:
                completion = groq_client.chat.completions.create(model=BRAIN_MODEL, messages=api_messages, temperature=0.7, stream=True)
                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content: yield content
            except Exception as e: yield f"Hiba: {str(e)}"
        return Response(stream_with_context(generate_groq()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
