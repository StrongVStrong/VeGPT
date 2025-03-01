from threading import Thread
from flask import Flask, request, jsonify, stream_with_context, Response
import itstheveggie
import sqlite3
import datetime
import os
import google.generativeai as genai
from flask_cors import CORS
import uuid

app = Flask(__name__)
app.secret_key = os.getenv("session_key")
MAX_CONTEXT_SIZE = os.getenv("max_context_size", 16)
CORS(app, supports_credentials=True)
API_KEY = os.getenv("GAPI_KEY") #Enter your Generative AI API key here/your .env file
genai.configure(api_key=API_KEY)
DATABASE = 'chat_sessions.db'

# Load descriptions
with open("veggie.txt", "r", encoding="utf8") as f1:
    base_description = f1.read()
    f1.close()

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

system_instruction = (
    base_description
)

default_message = "I'm sorry, but I can't assist with that topic."

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction=system_instruction
)

chat_session = model.start_chat(
  history=[]
)

def gemini_response(user_input):
    print("inside")
    response = chat_session.send_message(user_input)
    print("Response:", response)
    if response.candidates[0].finish_reason == "SAFETY":
        return default_message
    else:
        print("Inside gemini_response. User message:", user_input)
        full_response = ''.join(part.text for part in response.candidates[0].content.parts)
        return full_response

def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows access to columns by name (row['column_name'])
    return conn

def create_tables():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT
            )
        ''')
        
def save_message(session_id, role, content):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO chats (session_id, role, content)
            VALUES (?, ?, ?)''', (str(session_id), str(role), str(content)))
        conn.commit()
        
def get_chat_history(session_id):
    with get_db() as conn:
        cur = conn.execute('''
            SELECT role, content FROM chats
            WHERE session_id = ?''', (session_id,))
        return cur.fetchall()
    
def limit_context_size(chat_history, max_size):
    return chat_history[-max_size:] if len(chat_history) > max_size else chat_history
   
'''
def generate_audio(response_text):
    itstheveggie.gen_audio(response_text)
'''
@app.route('/chat', methods=['POST'])
def chat():
    
    data = request.get_json()
    print(data)

    if "user_input" not in data:
        return jsonify({"error": "No user input provided"}), 400

    user_message = data["user_input"]
    
    print(user_message)
    
    # Get or create a session ID
    session_id = request.cookies.get('SESS_ID')
    print(f"Session ID retrieved: {session_id}")
    
    if not session_id or len(session_id) != 16:
        # Generate a new session ID if not provided
        session_id = str(uuid.uuid4().hex[:16])
        response = jsonify({"message": "New session started"})
        response.set_cookie('SESS_ID', session_id, max_age=3600)  # 1 hour expiration
        print("Cookie set: ", session_id)
        return response
    
    if not session_id or len(session_id) != 16:
        return jsonify({"error": "You may not use this service without a valid session ID."}), 400
    
    # Retrieve chat history
    chat_history_db = get_chat_history(session_id)
    print(f"Chat history for session {session_id}: {chat_history_db}")
    chat_history = [{"role": row["role"], "content": row["content"]} for row in chat_history_db]
    # Append user message to chat history
    chat_history.append({"role": "user", "content": user_message})
    save_message(session_id, "user", user_message)
    # Limit context size
    limited_chat_history = limit_context_size(chat_history, MAX_CONTEXT_SIZE)
    # Add system instructions
    limited_chat_history.insert(0, {"role": "system", "content": base_description})
    
    # Get response from gemini.py
    print("Calling gemini_response with user message:", user_message)
    response_text = gemini_response(user_message)
    
    print(response_text)
    
    '''
    # Start audio generation in a background thread
    thread = Thread(target=generate_audio, args=(response_text,))
    thread.start()
    '''

    save_message(session_id, "assistant", response_text)

    return jsonify({"response": response_text})


@app.route('/')
def index():
    return 'API is now running.'


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
