from groq import Groq 
from json import load, dump
import datetime
from dotenv import dotenv_values

# Try different paths for .env file
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, ".env")

env_vars = dotenv_values(env_path) 



Username = env_vars.get('Username')
AssistantName = env_vars.get('AssistantName')
GroqAPIKey = env_vars.get('GroqAPIKey')

# Initialize Groq client only if API key is available
if GroqAPIKey:
    client = Groq(api_key=GroqAPIKey)
else:
    client = None
    print("Warning: GroqAPIKey not found in .env file")


System = f"""
Hello, I am {Username}. You are a highly accurate and advanced AI chatbot named {AssistantName} with real-time information from the internet.
*** Guidelines: ***
1. Do not tell the time unless asked.
2. Keep responses concise and to the point.
3. Always reply in English, regardless of the language of the question.
4. Provide direct answers without additional notes or mentioning your training data.
"""

SystemChatbot = [{"role": "system", "content": System}]


try:
    # Use correct path for Data directory
    data_path = os.path.join(project_root, "Data", "ChatLog.json")
    with open(data_path, "r") as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    messages = []

def RealTimeInformation():
    """Returns real-time date and time information."""
    current_date_time = datetime.datetime.now()
    return f"""Please use this real-time information if needed:
Day: {current_date_time.strftime('%A')}
Date: {current_date_time.strftime('%d')}
Month: {current_date_time.strftime('%B')}
Year: {current_date_time.strftime('%Y')}
Time: {current_date_time.strftime('%H:%M:%S')}
"""

def AnswerModifier(Answer):
    """Cleans up the chatbot's response for better readability."""
    return "\n".join([line for line in Answer.split("\n") if line.strip()])

def ChatBot(Query):
    """Handles user queries and maintains chat history."""
    global messages 

    try:
        # Check if client is available
        if client is None:
            return "Error: Groq API client not initialized. Please check your API key in the .env file."
       
        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=SystemChatbot + [{"role": "system", "content": RealTimeInformation()}] + messages[-3:],
            max_tokens=192,
            temperature=0.6,
            top_p=0.95,
            stream=True,
            stop=None
        )

       
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

       
        messages.append({"role": "assistant", "content": Answer})

        
        # Use correct path for Data directory
        data_path = os.path.join(project_root, "Data", "ChatLog.json")
        with open(data_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "I encountered an error, please try again."

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
