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

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])
    model = "meta-llama/llama-4-maverick-17b-128e-instruct" # Hardcoded as per request
    
    # Construct messages for the API
    # History format from frontend might need adjustment to match Groq's expected format
    # Groq expects: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    
    api_messages = []
    
    # Simple conversion of history if needed, or assume frontend sends compatible format
    # The reference frontend sends history. 
    # Let's trust the frontend sends a compatible structure or we adapt it here.
    # We will accept what the frontend sends but ensure the new message is added.
    
    # If history is empty, add system prompt or just start
    # The frontend handles 'modes' (geography, etc) by sending a greeting. 
    # We'll just append the new user message.
    
    # Flatten history to valid messages
    for msg in history:
        role = "assistant" if msg.get("role") == "model" or msg.get("role") == "ai" else "user"
        content = ""
        if "parts" in msg:
            content = msg["parts"][0]["text"]
        elif "content" in msg:
            content = msg["content"]
        else: 
            content = str(msg) # Fallback
            
        api_messages.append({"role": role, "content": content})

    api_messages.append({"role": "user", "content": user_message})

    def generate():
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=1,
                max_completion_tokens=1024,
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
