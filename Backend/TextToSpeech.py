import pygame
import random
import asyncio
import edge_tts
import os
import sys
from dotenv import dotenv_values

# Add the project root to the path to import GUI modules
current_dir = os.getcwd()
sys.path.append(current_dir)

env_vars = dotenv_values(".env") 
AssistantVoice = env_vars.get("AssistantVoice")

# Global reference to the main interface for heartbeat control
heartbeat_interface = None

def set_heartbeat_interface(interface):
    """Set the reference to the main interface for heartbeat control"""
    global heartbeat_interface
    heartbeat_interface = interface

async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+25%')  # Faster speech rate
    await communicate.save(r'Data\speech.mp3')
    

def TTS(Text, func=lambda r=None: True):
    # Start heartbeat animation
    if heartbeat_interface:
        try:
            heartbeat_interface.start_heartbeat()
        except Exception as e:
            print(f"Error starting heartbeat: {e}")
    
    while True:
        try:
            
            asyncio.run(TextToAudioFile(Text))
            
            
            pygame.mixer.init()
            
            
            pygame.mixer.music.load(r"Data\speech.mp3")
            
            
            pygame.mixer.music.play()
            
            
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(30)  # Faster tick rate
            
            # Stop heartbeat animation when speech ends
            if heartbeat_interface:
                try:
                    heartbeat_interface.stop_heartbeat()
                except Exception as e:
                    print(f"Error stopping heartbeat: {e}")
            
            return True
        except Exception as e:
            print(f"Error in TTS: {e}")
            
        finally:
            try:
                # Stop heartbeat animation in finally block as well
                if heartbeat_interface:
                    try:
                        heartbeat_interface.stop_heartbeat()
                    except Exception as e:
                        print(f"Error stopping heartbeat in finally: {e}")
                
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in finally block: {e}")
            

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".") 
    
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out.",
        "The rest of the text is now on the chat screen, please check it.",
        "You can see the rest of the text on the chat screen.",
        "The remaining part of the text is now on the chat screen.",
        "You'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen.",
        "Please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen.",
        "The next part of the text is on the chat screen.",
        "Please check the chat screen for more information.",
        "There's more text on the chat screen for you.",
        "Take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen.",
        "Check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text.",
        "There's more to see on the chat screen, please look.",
        "The chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out.",
        "Please review the chat screen for the rest of the text.",
        "Look at the chat screen for the complete answer."
    ]
    
    
    if len(Data) > 4 and len(Text) > 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
        
   
    else:
        TTS(Text, func)
        

if __name__ == "__main__":
    while True:
        
        TextToSpeech(input("Enter the text: "))