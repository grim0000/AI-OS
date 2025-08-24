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

# Import intelligent memory system
from Backend.IntelligentMemory import store_interaction, get_contextual_response
from Backend.CNNLogAnalyzer import CNNLogAnalyzer

System = f"""
Hello, I am {Username}. You are a highly accurate and advanced AI chatbot named {AssistantName} with real-time information from the internet.
*** Guidelines: ***
1. Do not tell the time unless asked.
2. Keep responses concise and to the point.
3. Always reply in English, regardless of the language of the question.
4. Provide direct answers without additional notes or mentioning your training data.
5. Use contextual memory to provide personalized responses.
"""

SystemChatbot = [{"role": "system", "content": System}]

# Keep minimal message history for immediate context (last 3 messages)
messages = []

# Initialize CNN Log Analyzer for bias optimization
try:
    cnn_analyzer = CNNLogAnalyzer()
    print("CNN Log Analyzer initialized successfully for ChatBot")
except Exception as e:
    print(f"Warning: Failed to initialize CNN Log Analyzer: {e}")
    cnn_analyzer = None

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
    """Handles user queries and maintains chat history with intelligent memory."""
    global messages 

    try:
        # Check if client is available
        if client is None:
            return "Error: Groq API client not initialized. Please check your API key in the .env file."
        
        # Get contextual information from memory
        contextual_info = get_contextual_response(Query)
        
        # Add contextual information to system prompt if available
        enhanced_system = System
        if contextual_info:
            enhanced_system += f"\n\nContext from previous conversations:{contextual_info}"
        
        enhanced_system_chatbot = [{"role": "system", "content": enhanced_system}]
       
        messages.append({"role": "user", "content": Query})

        # Add timeout handling for Groq API call
        import concurrent.futures
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    client.chat.completions.create,
                    model="llama-3.1-8b-instant",
                    messages=enhanced_system_chatbot + [{"role": "system", "content": RealTimeInformation()}] + messages[-3:],
                    max_tokens=192,
                    temperature=0.6,
                    top_p=0.95,
                    stream=False,
                    stop=None
                )
                completion = future.result(timeout=30)  # 30 second timeout
        except concurrent.futures.TimeoutError:
            print("⚠️ Groq API call timed out")
            return "I'm taking too long to respond. Please try again."
        except Exception as e:
            print(f"⚠️ Groq API error: {e}")
            return "I'm having trouble connecting right now. Please try again."

        Answer = completion.choices[0].message.content
        Answer = Answer.replace("</s>", "")

        # Apply CNN-based optimization if available
        if cnn_analyzer:
            try:
                # Analyze and optimize the response
                optimization_result = cnn_analyzer.analyze_and_optimize(Query, Answer)
                
                # Apply optimization suggestions
                if optimization_result['optimization_suggestions']:
                    print(f"🤖 CNN Optimization Suggestions: {optimization_result['optimization_suggestions']}")
                    
                    # Apply bias recommendations
                    bias_recs = optimization_result['bias_recommendations']
                    if bias_recs:
                        # Adjust response length if needed
                        optimal_length = bias_recs.get('optimal_response_length', len(Answer))
                        if abs(len(Answer) - optimal_length) > optimal_length * 0.3:
                            if len(Answer) < optimal_length and len(Answer.split()) < 20:
                                # Add more detail
                                Answer += "\n\nWould you like me to provide more specific information about this topic?"
                            elif len(Answer) > optimal_length * 1.5:
                                # Make more concise
                                sentences = Answer.split('. ')
                                if len(sentences) > 2:
                                    Answer = '. '.join(sentences[:2]) + '.'
                        
                        # Add follow-up questions if recommended
                        optimal_follow_ups = bias_recs.get('optimal_follow_ups', 0)
                        current_follow_ups = Answer.count('?')
                        if optimal_follow_ups > current_follow_ups and current_follow_ups == 0:
                            Answer += "\n\nIs there anything specific about this you'd like me to clarify?"
                
                # Predict response quality
                quality_score = cnn_analyzer.predict_response_quality(Query, Answer)
                print(f"🎯 Predicted Response Quality: {quality_score:.2f}")
                
                # If quality is low, try to improve
                if quality_score < 0.6:
                    print("⚠️ Low quality response detected, applying improvements...")
                    # Add engagement elements
                    if '?' not in Answer:
                        Answer += "\n\nDoes this answer your question?"
                
            except Exception as e:
                print(f"CNN optimization failed: {e}")

        messages.append({"role": "assistant", "content": Answer})

        # Store interaction in intelligent memory system
        store_interaction(
            user_input=Query,
            assistant_response=Answer,
            context={"source": "chatbot", "model": "llama-3.1-8b-instant"}
        )

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "I encountered an error, please try again."

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
