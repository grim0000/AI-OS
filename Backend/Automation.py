from AppOpener import close, open as appopen, give_appnames
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import os
import requests
import keyboard
import asyncio
import re
import ctypes
import os
import shutil
from send2trash import send2trash

env_vars = dotenv_values(".env")  
GroqAPIKey = env_vars.get('GroqAPIKey')


classes = ["zCubwf", "hgkElc", "LTKOO sY7ric","Z0LCW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "IZ6rdc", "05uR6d LTK00", "vlzY6d",
            "tw-Data-text tw-text-small tw-ta", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
            "LWkfKe", "VQF4g", "qv3wpe", "kno-rdesc", "SPZz6b" ]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36'


client = Groq(api_key=GroqAPIKey)


professional_responses = [ "Your Satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
                          "I'm at your service for any additional questions or support you may need-don't hesitate to reach out.",]

messages = []


SystemChatBot  = [
    {"role": "system", "content": f"Hello, I am {os.environ['Username']}, You are a content writer. You have to write content like letters, emails, reports, articles, applications and anything else that you are asked to do."},
]


def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    
   
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])
        
    
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"}) 
        
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream= True,
            stop=None
        )
        
        Answer = ""
        
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic: str = Topic.replace("Content", "") 
    ContentByAI = ContentWriterAI(Topic)
    
    
    with open(rf"Data/{Topic.lower().replace(' ', '')}.txt", "w", encoding='utf-8') as file:
        file.write(ContentByAI)
        file.close()
        
    OpenNotepad(rf"Data/{Topic.lower().replace(' ', '')}.txt")
    return True



def YouTubeSearch(Topic):
    Url4Serach = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Serach)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app):
    try:
       
        from AppOpener import open as appopen
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print(f"Failed to open '{app}' locally. Searching online...")

        def open_first_google_result(query):
            """ Uses Google's 'I'm Feeling Lucky' to open the first result directly and extracts the real URL. """
            google_search_url = f"https://www.google.com/search?q={query}+site+official&btnI=1"

            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(google_search_url, headers=headers, allow_redirects=False)  

            if response.status_code in [301, 302]:  
                redirected_url = response.headers.get("Location", "")

                
                match = re.search(r"q=(https?://[^\&]*)", redirected_url)
                if match:
                    final_url = match.group(1)
                    print(f"Redirected URL Found: {final_url}")
                    webbrowser.open(final_url)  
                    return True
                else:
                    print("Failed to extract final URL.")

            print("Failed to retrieve search results.")
            return False

       
        return open_first_google_result(app)
    
    

def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False


def list_files_and_folders(path):
    """List all files and folders in the specified directory"""
    if not os.path.exists(path):
        return f"❌ The folder '{path}' does not exist."

    items = os.listdir(path)
    return f"📂 Files and folders in {path}:\n" + "\n".join(items) if items else f"🚀 The folder '{path}' is empty."


def rename_item(old_path, new_path):
    """Rename a file or folder"""
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        return f"Renamed '{old_path}' to '{new_path}'."
    return f"Item '{old_path}' not found."


def move_item(src, dest):
    """Move a file or folder to a new location"""
    if os.path.exists(src):
        shutil.move(src, dest)
        return f" Moved '{src}' to '{dest}'."
    return f" '{src}' not found."

def delete_item(path):
    """Delete a file or folder (sends to Recycle Bin)"""
    if os.path.exists(path):
        send2trash(path)  
        return f" Moved '{path}' to Recycle Bin."
    return f" '{path}' not found."
   

def empty_recycle_bin():
    """Empties the Windows Recycle Bin"""
    try:
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)
        if result == 0:
            return "Recycle Bin has been cleaned successfully."
        else:
            return "Failed to clean the Recycle Bin."
    except Exception as e:
        return f"Error cleaning Recycle Bin: {str(e)}"


def SystemAutomation(command):
    
    if "clean up recycle bin" in command:
        return empty_recycle_bin()
    return " Command not recognized."

     

def System(command):
    
    
    def mute():
        keyboard.press_and_release("volume mute")
        
    def unmute():
        keyboard.press_and_release("volume mute")
        
    def volume_up():
        keyboard.press_and_release("volume up")
        
    def volume_down():
        keyboard.press_and_release("volume down")
        
    
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
        
    return True


async def TranslateAndExecute(commands: list[str]):
    funcs = []
    
    for command in commands:
        
        if command.startswith("open "): 
            
            if "open it" in command: 
                pass
            
            if "open file" in command: 
                pass
            
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open ")) 
                funcs.append(fun)
                
        elif command.startswith("general "): 
            pass
            
        elif command.startswith("realtime "): 
            pass
            
        elif command.startswith("close "): 
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close ")) 
            funcs.append(fun)
            
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play ")) 
            funcs.append(fun)
            
        elif command.startswith("content "): 
            fun = asyncio.to_thread(Content, command.removeprefix("content ")) 
            funcs.append(fun)
            
        elif command.startswith("google search "): 
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")) 
            funcs.append(fun)
            
        elif command.startswith("youtube search "): 
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")) 
            funcs.append(fun)
            
        elif command.startswith("system "): 
            fun = asyncio.to_thread(System, command.removeprefix("system ")) 
            funcs.append(fun)
            
        else:
            print(f"No Functions Found for: {command}")
            
    results = await asyncio.gather(*funcs) 
    
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result
            

async def Automation(commands: list[str]):
    
    async for result in TranslateAndExecute(commands):
        pass
    
    return True 