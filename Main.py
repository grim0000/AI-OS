from Frontend.ModernGUI import ( 
ModernGraphicalUserInterface as GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen, 
GetMicrophoneStatus,
GetAssistantStatus, 
SetMicrophoneStatus, TempDirectoryPath, AnswerModifier, QueryModifier)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation, SystemAutomation, smart_automation, enhanced_automation
from Backend.Chatbot import ChatBot
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import TextToSpeech, set_heartbeat_interface
from Backend.InteractiveDrafting import handle_drafting_request, get_current_drafting_question
from Backend.GmailIntegration import handle_gmail_request
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env") 
Username = env_vars.get("Username")
Assistantname = env_vars.get("AssistantName")
DefaultMessage = f'''{Username} : Hello, I am {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well.How can I help you?''' 

# List of available functions for automation
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "clean up"] 


def ShowDefaultChatIfNoChats():
    File = open('Data/ChatLog.json', 'r', encoding='utf-8')
    if len(File.read()) <= 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
            
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data/ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data
            
def ChatLogIntergration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
            
        formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
        formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")
        
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(AnswerModifier(formatted_chatlog))
            
          
def ShowChatOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data)) >0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File  = open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()
        
def IntialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntergration()
    ShowChatOnGUI()
    
    
IntialExecution()

def MainExecution(use_text_input=False, text_query=""):
    
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    
    if use_text_input:
        # Use text input instead of speech recognition
        Query = text_query
        SetAssistantStatus("Processing text...")
    else:
        # Use speech recognition
        SetAssistantStatus("Listening...")
        Query = SpeechRecognition()
        
        # Check if speech recognition was interrupted
        if Query is None:
            return False
        
        # Check if mic was turned off during speech recognition
        if GetMicrophoneStatus() == "False":
            return False
        
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    
    print("")
    print(f"Decision: {Decision}")
    print("")
    
    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    
    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    
    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True
    
    
    for queries in Decision:
        if " clean up " in queries:
            result = SystemAutomation(queries)
            print(result)
            ShowTextToScreen(f"{Assistantname}: {result}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(result)
            else:
                SetAssistantStatus("Ready")
            return True
        
        elif "smart_automation" in queries:
            SetAssistantStatus("Executing...")
            query = queries.replace("smart_automation", "").strip()
            result = enhanced_automation(query)  # Use enhanced automation
            print(f"🎯 Enhanced Automation Result: {result}")
            ShowTextToScreen(f"{Assistantname}: {result}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(result)
            else:
                SetAssistantStatus("Ready")
            return True
        
    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True
                
    if ImageExecution == True:
        
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
            
        try:
            p1 = subprocess.Popen(["python", "Backend/ImageGeneration.py"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
            
        except Exception as e:
            print(f"Error Starting ImageGeneration.py: {e}")
            
    if G and R or R:
        
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Username} : {Answer}")
        SetAssistantStatus("Answering")
        if not use_text_input:
            TextToSpeech(Answer)
        else:
            SetAssistantStatus("Ready")
        return True
    
    else:
        for Queries in Decision:
            
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                
                # Check if this is a drafting request
                drafting_response = handle_drafting_request(QueryModifier(QueryFinal))
                if drafting_response:
                    Answer = drafting_response
                else:
                    # Check if this is a Gmail request
                    gmail_response = handle_gmail_request(QueryModifier(QueryFinal))
                    if gmail_response:
                        Answer = gmail_response
                    else:
                        Answer = ChatBot(QueryModifier(QueryFinal))
                
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                
                # For text input, skip TTS
                if not use_text_input:
                    # Check if mic was turned off during processing
                    if GetMicrophoneStatus() == "False":
                        return False
                        
                    # Check for interruption during TTS
                    try:
                        TextToSpeech(Answer)
                    except:
                        # If TTS is interrupted, return False to stop processing
                        return False
                else:
                    # For text input, just update status
                    SetAssistantStatus("Ready")
                    
                return True
            
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ","")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                
                # For text input, skip TTS
                if not use_text_input:
                    # Check if mic was turned off during processing
                    if GetMicrophoneStatus() == "False":
                        return False
                        
                    # Check for interruption during TTS
                    try:
                        TextToSpeech(Answer)
                    except:
                        # If TTS is interrupted, return False to stop processing
                        return False
                else:
                    # For text input, just update status
                    SetAssistantStatus("Ready")
                    
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Goodbye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                if not use_text_input:
                    TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)
                
                
                
def FirstThread():
    
    while True:
        
        CurrentStatus = GetMicrophoneStatus()
        
        if CurrentStatus == "True":
            # Check for interrupt during execution
            try:
                result = MainExecution()
                # If MainExecution returns False, it was interrupted
                if result == False:
                    continue
            except KeyboardInterrupt:
                # Handle interruption
                SetMicrophoneStatus("False")
                SetAssistantStatus("Available...")
                continue
        else:
            AIStatus = GetAssistantStatus()
            
            if "Available..." in AIStatus:
                sleep(0.01)  # Ultra fast response time
                
            else:
                SetAssistantStatus("Available...")
                
def SecondThread():
    GraphicalUserInterface()
    
if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()


                                    
            
            
        