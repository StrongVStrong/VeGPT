import sqlite3

def query_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('chat_sessions.db')  # Path to your SQLite file
    cursor = conn.cursor()
    
    # Query the user_sessions table
    cursor.execute("SELECT * FROM user_sessions")
    rows = cursor.fetchall()
    
    # Print all rows
    for row in rows:
        print(row)
    
    # Close the connection
    conn.close()

# Run the query
query_database()
