# play.py
import vegito
import itstheveggie
import csv
import datetime

def export_history_to_csv(user_input, response, filename="chat_history.csv"):
    """Append user input and response to the chat history CSV file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a dictionary for the new log entry
    log_entry = {
        "Timestamp": timestamp,
        "User": user_input,
        "Vegito": response
    }
    
    # Check if the file already exists
    file_exists = False
    try:
        with open(filename, mode='r', newline='', encoding='utf-8'):
            file_exists = True
    except FileNotFoundError:
        pass  # File does not exist yet

    # Open the file and append the new log entry
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ["Timestamp", "User", "Vegito"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()  # Write header only if the file is new
        
        writer.writerow(log_entry)  # Write the user input and response to the CSV

def main():
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Come back soon.")
            break
        
        # Get response from gemini.py
        response_text = vegito.gemini_response(user_input)

        # Print Vegito's response
        print(f"Vegito: {response_text}")
        
        # Call play.py to generate and play the speech
        itstheveggie.gen_audio(response_text)
        
        export_history_to_csv(user_input, response_text)

if __name__ == "__main__":
    main()
