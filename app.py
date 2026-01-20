import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Gemini client
def get_gemini_client():
    api_keys_str = os.environ.get("GEMINI_API_KEY", "")
    api_keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
    if not api_keys:
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
    
    # Single model for both vision and reasoning
    MODEL_NAME = "gemini-2.0-flash" # High performance multimodal model
    
    # Base system instruction
    system_instruction = (
        "Te vagy VFG-AI, egy professzionális puskagép asszisztens. Mindig magyarul válaszolj. "
        "Válaszaid legyenek tömörek, lényegre törőek és mentesek mindenféle emojitól vagy hangulatjeltől. "
        "A kérdésekre a lehető legpontosabb és legátláthatóbb válaszokat add meg. A stílusod legyen hűvös és hatékony. "
        "FONTOS: Minden matematikai képletet és egyenletet LaTeX formátumban írj. "
        "Használj $$ ... $$ vagy \\[ ... \\] jelölést a kiemelt képletekhez, és $ ... $ vagy \\( ... \\) jelölést a szövegközi képletekhez. "
        "Például: $$ pV = nRT $$ vagy $ E = mc^2 $."
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

    # Build message parts for the current request
    message_parts = []
    
    # Add images if present
    for img_b64 in images:
        try:
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
        except Exception as e:
            print(f"Image processing error: {e}")

    # Add user message
    if user_message:
        message_parts.append({"text": user_message})

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

    # Add current message parts to history for the generation call
    # Note: contents in generate_content includes the full conversation
    full_contents = gemini_history + [{"role": "user", "parts": message_parts}]

    def generate():
        try:
            response_stream = client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=full_contents,
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
