from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os

# Initialize app
app = FastAPI()

# OpenAI client (API key will come from environment variable)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BOT_PERSONALITY = "You are a friendly chatbot named Esostrephes4. U ask relevant questions,incoporate humor,and make someone's day."
conversations = {}

class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest"

async def chat(user_id: str, message: str):
    if user_id not in conversations:
        conversations[user_id] = [
            {"role": "system", "content": BOT_PERSONALITY}
        ]

    conversations[user_id].append(
        {"role": "user", "content": message}
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversations[user_id],
        temperature=0.7,
        max_tokens=300,
    )

    bot_reply = response.choices[0].message.content
    conversations[user_id].append(
        {"role": "assistant", "content": bot_reply}
    )

    return bot_reply

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    reply = await chat(req.user_id, req.message)
    return {"reply": reply}

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chip Chatbot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(20px);
                
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .chat-container {
                width: 100%;
                max-width: 600px;
                background: #0F172A;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #f5f5f5;
                padding: 25px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }
            
            #chat {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f5f5f5;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .message {
                max-width: 75%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 10;
                    transform: translateY(0);
                }
            }
            
            .user-message {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: charcoal;
                align-self: flex-end;
                border-bottom-right-radius: 4px;
            }
            
            .bot-message {
                background: green;
                color: #333;
                align-self: flex-start;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 4px;
            }
            
            .message-label {
                font-weight: bold;
                margin-bottom: 4px;
                font-size: 12px;
                opacity: 0.8;
            }
            
            .input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 12px;
            }
            
            #msg {
                flex: 1;
                padding: 14px 18px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 15px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            #msg:focus {
                border-color: #667eea;
            }
            
            button {
                padding: 14px 28px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: yellow;
                border: none;
                border-radius: 25px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            .typing {
                padding: 12px 16px;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 18px;
                color: #888;
                font-style: italic;
                align-self: flex-start;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 0.6; }
                50% { opacity: 1; }
            }
            
            #chat::-webkit-scrollbar {
                width: 8px;
            }
            
            #chat::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            
            #chat::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }
            
            #chat::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                Chat with Chip 🤖
            </div>
            <div id="chat"></div>
            <div class="input-container">
                <input id="msg" placeholder="Type your message..." onkeypress="if(event.key==='Enter') send()">
                <button onclick="send()">Send</button>
            </div>
        </div>

        <script>
            function addMessage(text, sender) {
                const chat = document.getElementById("chat");
                const messageDiv = document.createElement("div");
                messageDiv.className = "message " + (sender === "user" ? "user-message" : "bot-message");
                messageDiv.textContent = text;
                chat.appendChild(messageDiv);
                chat.scrollTop = chat.scrollHeight;
            }
            
            function showTyping() {
                const chat = document.getElementById("chat");
                const typing = document.createElement("div");
                typing.className = "typing";
                typing.id = "typing-indicator";
                typing.textContent = "Chip is typing...";
                chat.appendChild(typing);
                chat.scrollTop = chat.scrollHeight;
            }
            
            function hideTyping() {
                const typing = document.getElementById("typing-indicator");
                if (typing) typing.remove();
            }

            async function send() {
                let msg = document.getElementById("msg").value.trim();
                if (!msg) return;

                addMessage(msg, "user");
                document.getElementById("msg").value = "";
                
                showTyping();

                try {
                    let res = await fetch("/chat", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({message: msg, user_id: "guest"})
                    });

                    let data = await res.json();
                    hideTyping();
                    addMessage(data.reply, "bot");
                } catch (error) {
                    hideTyping();
                    addMessage("Sorry, something went wrong. Please try again!", "bot");
                }
            }
            
            // Welcome message
            addMessage("Hey! I'm Chip, your friendly chatbot. How can I help you today?", "bot");
        </script>
    </body>
    </html>
    """
