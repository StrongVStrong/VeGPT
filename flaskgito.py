from threading import Thread
from flask import Flask, request, jsonify, session
import vegito
import itstheveggie
import sqlite3
import datetime
import os
from flask_cors import CORS
import uuid

app = Flask(__name__)
app.secret_key = os.getenv("session_key")
CORS(app)
DATABASE = 'chat_sessions.db'

def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows access to columns by name (row['column_name'])
    return conn

def create_tables():
    """Create the necessary tables if they don't exist."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_input TEXT,
                response TEXT,
                session_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
def get_or_create_session():
    """Get or create a session ID."""
    if 'session_id' not in session:
        # Create a new session ID if it doesn't exist in Flask's session
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sessions (created_at) VALUES (CURRENT_TIMESTAMP)")
            session_id = cursor.lastrowid  # Get the last inserted session_id
            session['session_id'] = session_id  # Store it in Flask's session
    return session['session_id']
        
'''
def generate_audio(response_text):
    itstheveggie.gen_audio(response_text)
'''
@app.route('/chat', methods=['POST'])
def chat():
    
    data = request.get_json()

    if "user_input" not in data:
        return jsonify({"error": "No user input provided"}), 400

    user_input = data["user_input"]
    
    # Get or create a session ID
    session_id = get_or_create_session()
    
    # Get response from gemini.py (via vegito)
    response_text = vegito.gemini_response(user_input)
    
    # Save user input and response to the database, associated with the session ID
    with get_db() as conn:
        conn.execute("INSERT INTO user_sessions (user_input, response, session_id) VALUES (?, ?, ?)",(user_input, response_text, session_id))
    '''
    # Start audio generation in a background thread
    thread = Thread(target=generate_audio, args=(response_text,))
    thread.start()
    '''
    # Return the response immediately
    return jsonify({"response": response_text})


@app.route('/')
def index():
    return 'API is now running.'


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
