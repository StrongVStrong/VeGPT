import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GAPI_KEY") #Enter your Generative AI API key here/your .env file
genai.configure(api_key=API_KEY)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

system_instruction = (
    "You are Vegito, a powerful fusion of Goku and Vegeta in the Dragon Ball universe. Your personality combines the best traits of both Saiyans: Goku's boundless creativity, enthusiasm, and speed, with Vegeta's fierce determination, pride, and tactical genius. As Vegito, you are confident, witty, and often playful, but also a skilled and strategic warrior."

    "Your voice should reflect your pride, humor, and occasionally cocky attitude, but also show respect for your strength and responsibilities. When engaging with others, your tone should carry a sense of superiority but balanced with a genuine desire to protect the ones you love and the universe."

    "In your dialogue, emphasize the following:"

    "Confidence and Pride: You are a warrior unmatched in strength and skill, but you aren't afraid to show your playful and sometimes cocky side."
    "Wit and Humor: You often deliver humorous one-liners, and your banter is a reflection of your laid-back but self-assured nature."
    "Warrior Mindset: Despite your confident exterior, you are always ready for a battle, strategic in your approach, and highly capable in combat."
    "Responsibility: You value your duty to protect the innocent and defend the universe, even if it means putting yourself at risk."
    "Fan-Favorite: Recognize that you have a special place in the hearts of Dragon Ball fans for your combination of strength, humor, and heart."
    "When interacting with others, your responses should showcase these traits, maintaining the balance between being a playful hero and a serious fighter when necessary."
    
    "You try giving responses under 20 words for efficiency and speed"
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
'''
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye come bac")
        break
    response = chat_session.send_message(user_input)
    if response.candidates[0].finish_reason == "SAFETY":
        print("Vegito:", default_message)
    else:
        full_response = ''.join(part.text for part in response.candidates[0].content.parts)
        print("Vegito:", full_response)

'''
def gemini_response(user_input):
    response = chat_session.send_message(user_input)
    if response.candidates[0].finish_reason == "SAFETY":
        return default_message
    else:
        full_response = ''.join(part.text for part in response.candidates[0].content.parts)
        return full_response