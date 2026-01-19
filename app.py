import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Groq client
# Note: In production (Vercel), ensure GROQ_API_KEY is set in the environment variables.
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
    model = "meta-llama/llama-4-maverick-17b-128e-instruct" 
    
    # Base system instruction
    system_instruction = "Te vagy VFG-AI, egy professzionális puskagép asszisztens. Mindig magyarul válaszolj. Válaszaid legyenek tömörek, lényegre törőek és mentesek mindenféle emojitól vagy hangulatjeltől. A kérdésekre a lehető legpontosabb és legátláthatóbb válaszokat add meg. A stílusod legyen hűvös és hatékony."

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

    api_messages = [{"role": "system", "content": system_instruction}]
    
    # Process history
    for msg in history:
        role = "assistant" if msg.get("role") == "model" or msg.get("role") == "ai" else "user"
        content_block = []
        
        # Text content
        text_content = ""
        if "parts" in msg:
            text_content = msg["parts"][0]["text"]
        elif "content" in msg:
            text_content = msg["content"]
        else: 
            text_content = str(msg)
            
        content_block.append({"type": "text", "text": text_content})
            
        # Image content in history (optional, simpler to ignore old images to save tokens/bandwidth unless critical)
        # But if we did:
        if msg.get("images"):
             for img_b64 in msg.get("images"):
                 content_block.append({
                     "type": "image_url",
                     "image_url": {
                         "url": img_b64
                     }
                 })

        # If pure text, can send string. If mixed, must be list of objects.
        # Groq Llama 3.2 Vision supports list of content blocks.
        if len(content_block) == 1 and content_block[0]["type"] == "text":
            api_messages.append({"role": role, "content": content_block[0]["text"]})
        else:
            api_messages.append({"role": role, "content": content_block})

    # Process current message
    current_message_content = []
    if user_message:
        current_message_content.append({"type": "text", "text": user_message})
    
    for img_b64 in images:
        current_message_content.append({
            "type": "image_url",
            "image_url": {
                "url": img_b64
            }
        })

    api_messages.append({"role": "user", "content": current_message_content})

    def generate():
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=1,
                top_p=1,
                stream=True,
                stop=None
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
