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
from Backend.PrivacyProtectedEmail import PrivacyProtectedEmailSystem
from Backend.ReinforcementLearningSystem import rl_system
from Backend.FeedbackHandler import handle_feedback_request, process_pending_feedback
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

# Initialize privacy-protected email system
privacy_email_system = PrivacyProtectedEmailSystem() 


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
    
    # Check for privacy-protected email requests FIRST (highest priority)
    QueryLower = Query.lower()
    
    # Check if this is a privacy-protected email request
    if any(marker in Query for marker in ["<sub>", "<body>", "subject", "body"]) and any(cmd in QueryLower for cmd in ["draft", "compose", "send"]):
        SetAssistantStatus("Processing Privacy-Protected Email...")
        try:
            # Handle the privacy-protected email request
            response = privacy_email_system.handle_email_request(Query)
            Answer = response
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(Answer)
            else:
                SetAssistantStatus("Ready")
            return True
        except Exception as e:
            Answer = f"Privacy-protected email system error: {str(e)}"
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(Answer)
            else:
                SetAssistantStatus("Ready")
            return True
    
    # Check if user wants to open the email dialog
    elif "open email dialog" in QueryLower or "show email dialog" in QueryLower:
        SetAssistantStatus("Opening Email Dialog...")
        try:
            # Get the email content from the privacy system
            response = privacy_email_system.open_email_dialog()
            
            # Check if response is a dictionary (success) or string (error)
            if isinstance(response, dict) and response.get("action") == "open_email_dialog":
                # Set the email dialog request for the main GUI thread to process
                try:
                    from Frontend.ModernGUI import set_email_dialog_request
                    set_email_dialog_request(response)
                    Answer = "Email dialog request sent to main thread. The dialog will open shortly."
                except Exception as e:
                    Answer = f"Error setting dialog request: {str(e)}"
            else:
                # Error response
                Answer = response
                
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(Answer)
            else:
                SetAssistantStatus("Ready")
            return True
        except Exception as e:
            Answer = f"Error opening email dialog: {str(e)}"
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(Answer)
            else:
                SetAssistantStatus("Ready")
            return True
    
    # Direct Gmail command recognition (bypasses AI model to avoid rate limits)
    elif any(gmail_cmd in QueryLower for gmail_cmd in ["gmail", "email", "send email", "setup gmail"]):
        SetAssistantStatus("Processing Gmail...")
        
        # Regular Gmail command
        gmail_response = handle_gmail_request(Query)
        if gmail_response:
            Answer = gmail_response
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(Answer)
            else:
                SetAssistantStatus("Ready")
            return True
    
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
        
        elif "show learning stats" in queries or "learning statistics" in queries:
            try:
                stats = rl_system.get_learning_stats()
                result = f"Learning Statistics:\nTotal Feedback: {stats['total_feedback']}\nPositive: {stats['positive_feedback']}\nNegative: {stats['negative_feedback']}\nContexts: {stats['total_contexts']}"
                print(result)
                ShowTextToScreen(f"{Assistantname}: {result}")
                SetAssistantStatus("Answering...")
                if not use_text_input:
                    TextToSpeech(result)
                else:
                    SetAssistantStatus("Ready")
                return True
            except Exception as e:
                result = f"Error getting learning stats: {e}"
                ShowTextToScreen(f"{Assistantname}: {result}")
                return True
        
        elif "reset learning" in queries or "clear preferences" in queries:
            try:
                rl_system.reset_learning()
                result = "Learning preferences have been reset to default values."
                print(result)
                ShowTextToScreen(f"{Assistantname}: {result}")
                SetAssistantStatus("Answering...")
                if not use_text_input:
                    TextToSpeech(result)
                else:
                    SetAssistantStatus("Ready")
                return True
            except Exception as e:
                result = f"Error resetting learning: {e}"
                ShowTextToScreen(f"{Assistantname}: {result}")
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
                
                # Check if this is a feedback request first
                feedback_response = handle_feedback_request(QueryModifier(QueryFinal))
                if feedback_response:
                    Answer = feedback_response
                    # Process the feedback through RL system
                    process_pending_feedback()
                else:
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
            elif "gmail" in Queries:
                SetAssistantStatus("Processing Gmail...")
                QueryFinal = Queries.replace("gmail", "")
                gmail_response = handle_gmail_request(QueryModifier(QueryFinal))
                if gmail_response:
                    Answer = gmail_response
                else:
                    Answer = "I didn't understand that Gmail command. Try 'gmail help' for available commands."
                
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                if not use_text_input:
                    TextToSpeech(Answer)
                else:
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


                                    
            
            
        