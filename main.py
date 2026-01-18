from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os

# Initialize app
app = FastAPI()

# OpenAI client (API key will come from environment variable)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BOT_PERSONALITY = "You are a friendly chatbot named Chip."
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

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=conversations[user_id],
        temperature=0.7,
        max_output_tokens=300,
    )

    bot_reply = response.output_text
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
    </head>
    <body>
        <h2>Chat with Chip 🤖</h2>
        <div id="chat" style="height:300px; border:1px solid #ccc; overflow:auto; padding:10px;"></div>
        <input id="msg" placeholder="Type message..." style="width:80%">
        <button onclick="send()">Send</button>

        <script>
            async function send() {
                let msg = document.getElementById("msg").value;
                if (!msg) return;

                document.getElementById("chat").innerHTML += "<p><b>You:</b> " + msg + "</p>";

                let res = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: msg, user_id: "guest"})
                });

                let data = await res.json();
                document.getElementById("chat").innerHTML += "<p><b>Chip:</b> " + data.reply + "</p>";
                document.getElementById("msg").value = "";
            }
        </script>
    </body>
    </html>
    """
