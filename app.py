import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

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
    
    # Models
    VISION_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
    BRAIN_MODEL = "groq/compound"
    
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

    # --- STEP 1: The Eyes (Maverick 4) if images are present ---
    image_context = ""
    if images:
        try:
            vision_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Elemezd a képet függetlenül a tantárgytól. Készíts 1:1 arányú vizuális rekonstrukciót. A grafikonokat ne csak említsd meg, hanem írd le a tengelyeiket, a görbék alakját, a metszéspontokat és az adatokat úgy, mintha egy vak embernek magyaráznád el, akinek meg kell oldania a feladatot. A matematikai képleteket konvertáld LaTeX formátumba. Minden szöveget, számot, ábrát, diagramot, táblázatot és grafikus elemet írj le részletesen, hogy a következő AI modell teljes mértékben megértse a képet anélkül, hogy látná azt. Rekonstruálj mindent digitálisan, hogy az információ 100%-ban átadható legyen."},
                    ]
                }
            ]
            for img_b64 in images:
                vision_messages[0]["content"].append({"type": "image_url", "image_url": {"url": img_b64}})
            
            vision_response = client.chat.completions.create(
                model=VISION_MODEL,
                messages=vision_messages,
                temperature=0.0 # Zero temperature for maximum accuracy and 1:1 reconstruction
            )
            image_context = vision_response.choices[0].message.content
        except Exception as e:
            print(f"Vision extraction error: {e}")
            image_context = "Hiba történt a kép feldolgozása során."

    # --- STEP 2: The Brain (Groq Compound) ---
    api_messages = [{"role": "system", "content": system_instruction}]
    
    # Process history
    for msg in history:
        role = "assistant" if msg.get("role") == "model" or msg.get("role") == "ai" else "user"
        content = ""
        if "parts" in msg:
            content = msg["parts"][0]["text"]
        elif "content" in msg:
            content = msg["content"]
        else: 
            content = str(msg)
        api_messages.append({"role": role, "content": content})

    # Add current message with image context
    final_user_content = user_message
    if image_context:
        final_user_content = f"DIGITÁLIS REKONSTRUKCIÓ A KÉPBŐL (teljes 1:1 arányú átírás, kezeld úgy mintha látnád a képet):\n\n{image_context}\n\n---\n\nFELHASZNÁLÓ KÉRDÉSE: {user_message}"
    
    api_messages.append({"role": "user", "content": final_user_content})

    def generate():
        try:
            completion = client.chat.completions.create(
                model=BRAIN_MODEL,
                messages=api_messages,
                temperature=0.7,
                stream=True
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except Exception as e:
            yield f"Hiba: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
