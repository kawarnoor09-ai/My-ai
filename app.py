import os
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # <-- Swap this with your actual OpenRouter API key
)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My AI Bot</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #121212; color: #e0e0e0; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background: #1e1e1e; padding: 15px; text-align: center; border-bottom: 1px solid #2d2d2d; font-size: 1.2rem; font-weight: bold; color: #fff; }
        .chat-container { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .message { padding: 12px 16px; border-radius: 18px; max-width: 75%; word-wrap: break-word; line-height: 1.4; }
        .user { background: #007bff; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #2a2a2a; color: #f0f0f0; align-self: flex-start; border-bottom-left-radius: 4px; }
        .input-area { display: flex; padding: 15px; background: #1e1e1e; gap: 10px; border-top: 1px solid #2d2d2d; }
        input { flex: 1; padding: 14px; border-radius: 25px; border: 1px solid #333; background: #252525; color: white; outline: none; font-size: 16px; }
        input::placeholder { color: #777; }
        button { background: #007bff; color: white; border: none; padding: 0 24px; border-radius: 25px; cursor: pointer; font-size: 16px; font-weight: bold; transition: background 0.2s; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>

    <header>🤖 Nex N2 Pro AI Chatbot</header>

    <div class="chat-container" id="chat">
        <div class="message bot">👋 Yo! I'm live on the web. Ask me anything!</div>
    </div>

    <div class="input-area">
        <input type="text" id="userInput" placeholder="Message your AI..." onkeydown="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        let conversationHistory = [{"role": "system", "content": "You are a helpful, chill AI assistant."}];

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chat = document.getElementById('chat');
            const text = input.value.trim();
            if (!text) return;

            // Display User Message
            chat.innerHTML += `<div class="message user">${text}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            // Update History
            conversationHistory.push({"role": "user", "content": text});

            // Create temporary typing bubble
            const botBubbleId = 'typing-' + Date.now();
            chat.innerHTML += `<div class="message bot" id="${botBubbleId}">🤔 Thinking...</div>`;
            chat.scrollTop = chat.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: conversationHistory })
                });
                const data = await response.json();
                
                // Replace typing bubble with actual reply
                const botBubble = document.getElementById(botBubbleId);
                botBubble.innerText = data.reply;
                
                conversationHistory.push({"role": "assistant", "content": data.reply});
                chat.scrollTop = chat.scrollHeight;
            } catch (error) {
                document.getElementById(botBubbleId).innerHTML = `<span style="color: #ff4a4a;">Error connecting to server.</span>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_history = data.get('messages', [])
    
    try:
        response = client.chat.completions.create(
            model="nex-agi/nex-n2-pro:free",
            messages=user_history
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    # Dynamically reads the port Render gives it, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
