from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get('Username')
AssistantName = env_vars.get('AssistantName')
GroqAPIKey = env_vars.get('GroqAPIKey')

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}. You are {AssistantName}, an advanced AI with real-time search capability.
*** Always provide answers professionally with proper grammar, punctuation, and complete sentences. ***
*** Answer based on provided search data and past user inputs. ***
*** Use contextual memory to provide personalized responses. ***
"""

# Import intelligent memory system
from Backend.IntelligentMemory import store_interaction, get_contextual_response

# Keep minimal message history for immediate context
messages = []


def GoogleSearch(query):
    try:
        # Enhanced search for financial/stock data
        if any(keyword in query.lower() for keyword in ['stock', 'market', 'nasdaq', 'dow', 's&p', 'price', 'trading']):
            # Use a more reliable search method for financial data
            import requests
            from bs4 import BeautifulSoup
            
            # Try to get real-time stock data
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            try:
                response = requests.get(search_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for stock price information
                    price_elements = soup.find_all(['span', 'div'], class_=lambda x: x and any(term in x.lower() for term in ['price', 'value', 'stock', 'market']))
                    
                    if price_elements:
                        stock_info = f"Real-time search results for '{query}':\n"
                        for i, element in enumerate(price_elements[:5]):
                            text = element.get_text().strip()
                            if text and len(text) > 10:
                                stock_info += f"• {text}\n"
                        return stock_info
            except:
                pass
        
        # Fallback to regular search
        try:
            from googlesearch import search as google_search
            results = list(google_search(query, num_results=3))
        except ImportError:
            # If googlesearch is not available, use web browser fallback
            import webbrowser
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"I've opened a web search for '{query}' in your browser."
        Answer = f"The search results for '{query}' are:\n[start]\n"

        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

        Answer += "[end]"
        return Answer
        
    except Exception as e:
        print(f"Search error: {e}")
        return f"I couldn't find real-time information for '{query}'. Please try a different search term or check your internet connection."


def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer


SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I assist you today?"}
]


def Information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year =  current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-Time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds,\n"
    return data



def RealtimeSearchEngine(prompt):
    global messages  

    # Get contextual information from memory
    contextual_info = get_contextual_response(prompt)
    
    # Add contextual information to system prompt if available
    enhanced_system = System
    if contextual_info:
        enhanced_system += f"\n\nContext from previous conversations:{contextual_info}"
    
    enhanced_system_chatbot = [{"role": "system", "content": enhanced_system}]

    messages.append({"role": "user", "content": prompt})

    search_results = GoogleSearch(prompt)

    full_messages = enhanced_system_chatbot + [{"role": "system", "content": search_results}] + messages

    # Add timeout handling for Groq API call
    import concurrent.futures
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                client.chat.completions.create,
                model="llama-3.1-8b-instant",
                messages=full_messages,
                max_tokens=384,
                temperature=0.6,
                top_p=0.95,
                stream=False,
                stop=None
            )
            completion = future.result(timeout=30)  # 30 second timeout
    except concurrent.futures.TimeoutError:
        print("⚠️ Groq API call timed out")
        return "I'm taking too long to search for that information. Please try again."
    except Exception as e:
        print(f"⚠️ Groq API error: {e}")
        return "I'm having trouble searching right now. Please try again."

    Answer = completion.choices[0].message.content
    Answer = Answer.strip().replace("</s>", "")

    messages.append({"role": "assistant", "content": Answer})

    # Store interaction in intelligent memory system
    store_interaction(
        user_input=prompt,
        assistant_response=Answer,
        context={"source": "realtime_search", "search_results": search_results[:200]}  # Store first 200 chars of search results
    )

    return AnswerModifier(Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))