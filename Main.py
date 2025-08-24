from Frontend.ModernGUI import ( 
ModernGraphicalUserInterface as GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen, 
GetMicrophoneStatus,
GetAssistantStatus, 
SetMicrophoneStatus, TempDirectoryPath, AnswerModifier, QueryModifier)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation, SystemAutomation, smart_automation, enhanced_automation, make_conversational_response
from Backend.Chatbot import ChatBot
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import TextToSpeech, set_heartbeat_interface
from Backend.InteractiveDrafting import handle_drafting_request, get_current_drafting_question
from Backend.GmailIntegration import handle_gmail_request
from dotenv import dotenv_values
from asyncio import run, TimeoutError as AsyncTimeoutError
from time import sleep
import subprocess
import threading
import json
import os
import signal
import time

# Global subprocesses list for proper cleanup
subprocesses = []

env_vars = dotenv_values(".env") 
Username = env_vars.get("Username")
Assistantname = env_vars.get("AssistantName")
DefaultMessage = f'''{Username} : Hello, I am {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well.How can I help you?''' 

# List of available functions for automation
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "clean up"] 

# Add timeout for API calls to prevent freezing
API_TIMEOUT = 30  # seconds

def cleanup_subprocesses():
    """Clean up any running subprocesses to prevent hanging"""
    global subprocesses
    for proc in subprocesses:
        try:
            if proc.poll() is None:  # Process is still running
                proc.terminate()
                proc.wait(timeout=5)  # Wait up to 5 seconds
        except:
            try:
                proc.kill()  # Force kill if terminate doesn't work
            except:
                pass
    subprocesses.clear()

def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls with timeout and error handling"""
    try:
        # Add timeout to the function call
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result(timeout=API_TIMEOUT)
    except concurrent.futures.TimeoutError:
        print(f"⚠️ API call timed out after {API_TIMEOUT} seconds")
        return f"I'm taking too long to respond. Please try again."
    except Exception as e:
        print(f"⚠️ API call failed: {e}")
        return f"I encountered an error. Please try again."


def ShowDefaultChatIfNoChats():
    # Check if intelligent memory system has any data
    try:
        from Backend.IntelligentMemory import intelligent_memory
        memories = intelligent_memory.get_relevant_memories("", limit=1)
        if not memories:
            # No memories found, show default message
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")
                
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)
        else:
            # Has memories, load them
            ChatLogIntergration()
    except Exception as e:
        print(f"⚠️ Error checking intelligent memory: {e}")
        # Fallback to default message
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
            
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadIntelligentMemory():
    try:
        from Backend.IntelligentMemory import intelligent_memory
        memories = intelligent_memory.get_relevant_memories("", limit=50)  # Get last 50 memories
        return memories
    except Exception as e:
        print(f"⚠️ Error reading intelligent memory: {e}")
        return []
            
def ChatLogIntergration():
    memories = ReadIntelligentMemory()
    formatted_chatlog = ""
    
    for memory in memories:
        formatted_chatlog += f"User: {memory.user_input}\n"
        formatted_chatlog += f"Assistant: {memory.assistant_response}\n"
        
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
    
    # Check for Gmail commands FIRST - bypass all AI classification
    if any(gmail_cmd in Query.lower() for gmail_cmd in ["gmail", "email", "send email", "draft email", "setup gmail", "send an email with subject", "draft an email", "send an email with the subject"]):
        print(f"📧 Gmail command detected: {Query}")
        SetAssistantStatus("Processing Gmail...")
        gmail_response = handle_gmail_request(QueryModifier(Query))
        if gmail_response is not None:
            Answer = str(gmail_response)  # Ensure it's a string
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(Answer)
            else:
                SetAssistantStatus("Ready")
            return True
        else:
            error_msg = "I couldn't process that Gmail command. Please try again."
            ShowTextToScreen(f"{Assistantname}: {error_msg}")
            SetAssistantStatus("Ready")
            return True
    
    SetAssistantStatus("Thinking...")
    
    # Use safe API call with timeout
    try:
        Decision = safe_api_call(FirstLayerDMM, Query)
        if isinstance(Decision, str):
            # If API call returned error message, handle it
            ShowTextToScreen(f"{Assistantname} : {Decision}")
            SetAssistantStatus("Ready")
            return True
    except Exception as e:
        print(f"⚠️ Decision making failed: {e}")
        error_msg = "I'm having trouble understanding that. Could you try rephrasing?"
        ShowTextToScreen(f"{Assistantname} : {error_msg}")
        SetAssistantStatus("Ready")
        return True
    
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
            try:
                result = SystemAutomation(queries)
                print(result)
                ShowTextToScreen(f"{Assistantname}: {result}")
                SetAssistantStatus("Answering...")
                if not use_text_input:
                    TextToSpeech(result)
                else:
                    SetAssistantStatus("Ready")
                return True
            except Exception as e:
                print(f"Clean up failed: {e}")
                error_msg = f"I couldn't complete the cleanup. {make_conversational_response(str(e), 'cleanup')}"
                ShowTextToScreen(f"{Assistantname}: {error_msg}")
                if not use_text_input:
                    TextToSpeech(error_msg)
                else:
                    SetAssistantStatus("Ready")
                return True
        
        elif "smart_automation" in queries:
            SetAssistantStatus("Executing...")
            query = queries.replace("smart_automation", "").strip()
            
            # If not Gmail, proceed with normal smart automation
            try:
                result = enhanced_automation(query)  # Use enhanced automation
                print(f"🎯 Enhanced Automation Result: {result}")
                ShowTextToScreen(f"{Assistantname}: {result}")
                SetAssistantStatus("Answering...")
                if not use_text_input:
                    TextToSpeech(result)
                else:
                    SetAssistantStatus("Ready")
                return True
            except Exception as e:
                print(f"Smart automation failed: {e}")
                error_msg = f"I couldn't complete that automation. {make_conversational_response(str(e), 'automation')}"
                ShowTextToScreen(f"{Assistantname}: {error_msg}")
                if not use_text_input:
                    TextToSpeech(error_msg)
                else:
                    SetAssistantStatus("Ready")
                return True
        
    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                try:
                    result = run(Automation(list(Decision)))
                    if result:
                        TaskExecution = True
                except Exception as e:
                    print(f"Task execution failed: {e}")
                    error_msg = f"I couldn't complete that task. {make_conversational_response(str(e), 'task')}"
                    ShowTextToScreen(f"{Assistantname}: {error_msg}")
                    if not use_text_input:
                        TextToSpeech(error_msg)
                    else:
                        SetAssistantStatus("Ready")
                    return True
                
    if ImageExecution == True:
        
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
            
        try:
            p1 = subprocess.Popen(["python", "Backend/ImageGeneration.py"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
            
            # Set a timeout for the subprocess
            def timeout_kill():
                time.sleep(60)  # 60 second timeout
                if p1.poll() is None:
                    p1.terminate()
                    print("⚠️ Image generation timed out and was terminated")
            
            timeout_thread = threading.Thread(target=timeout_kill, daemon=True)
            timeout_thread.start()
            
        except Exception as e:
            print(f"Error Starting ImageGeneration.py: {e}")
            
    if G and R or R:
        
        SetAssistantStatus("Searching...")
        try:
            Answer = safe_api_call(RealtimeSearchEngine, QueryModifier(Mearged_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            if not use_text_input:
                TextToSpeech(Answer)
            else:
                SetAssistantStatus("Ready")
            return True
        except Exception as e:
            print(f"Real-time search failed: {e}")
            error_msg = f"I couldn't get real-time information for that. {make_conversational_response(str(e), 'search')}"
            ShowTextToScreen(f"{Assistantname} : {error_msg}")
            if not use_text_input:
                TextToSpeech(error_msg)
            else:
                SetAssistantStatus("Ready")
            return True
    
    else:
        for Queries in Decision:
            
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                
                # Check if this is a drafting request
                try:
                    drafting_response = handle_drafting_request(QueryModifier(QueryFinal))
                    if drafting_response:
                        Answer = drafting_response
                    else:
                        Answer = safe_api_call(ChatBot, QueryModifier(QueryFinal))
                except Exception as e:
                    print(f"ChatBot failed: {e}")
                    Answer = f"I'm having trouble processing that right now. {make_conversational_response(str(e), 'chat')}"
                
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
                try:
                    Answer = safe_api_call(RealtimeSearchEngine, QueryModifier(QueryFinal))
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
                except Exception as e:
                    print(f"Real-time search failed: {e}")
                    error_msg = f"I couldn't get real-time information for that. {make_conversational_response(str(e), 'search')}"
                    ShowTextToScreen(f"{Assistantname} : {error_msg}")
                    if not use_text_input:
                        TextToSpeech(error_msg)
                    else:
                        SetAssistantStatus("Ready")
                    return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Goodbye!"
                Answer = safe_api_call(ChatBot, QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                if not use_text_input:
                    TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                cleanup_subprocesses()  # Clean up before exit
                os._exit(1)
    
    # Final fallback - if nothing was executed, return to listening state
    if not TaskExecution and not ImageExecution:
        fallback_msg = "I'm not sure how to help with that. Could you try rephrasing your request?"
        ShowTextToScreen(f"{Assistantname} : {fallback_msg}")
        if not use_text_input:
            TextToSpeech(fallback_msg)
        else:
            SetAssistantStatus("Ready")
        return True
                
                
                
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
            except Exception as e:
                # Handle any other exceptions to prevent thread crashes
                print(f"⚠️ Thread error: {e}")
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
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Shutting down gracefully...")
        cleanup_subprocesses()
        os._exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    
    try:
        SecondThread()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        cleanup_subprocesses()
    except Exception as e:
        print(f"⚠️ GUI error: {e}")
        cleanup_subprocesses()


                                    
            
            
        