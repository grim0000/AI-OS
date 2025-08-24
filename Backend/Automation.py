from AppOpener import close, open as appopen, give_appnames
from webbrowser import open as webopen
# Fix pywhatkit import to avoid search function issues
try:
    from pywhatkit import playonyt
    # Import search function separately to avoid conflicts
    import pywhatkit.core.core as pywhatkit_core
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False
    print("⚠️ pywhatkit not available")
from dotenv import dotenv_values
from groq import Groq
import webbrowser
import subprocess
import os
import requests
import keyboard
import asyncio
import re
import ctypes
import shutil
from send2trash import send2trash
import winreg
import json
import time
import random

# Import screen vision capabilities
try:
    from Backend.ScreenVision import capture_and_analyze, get_smart_click_position, start_screen_monitoring
    SCREEN_VISION_AVAILABLE = True
    print("🖥️ Screen Vision System loaded successfully")
except ImportError as e:
    print(f"⚠️ Screen Vision not available: {e}")
    SCREEN_VISION_AVAILABLE = False

# Import Excel automation
try:
    from Backend.ExcelAutomation import handle_excel_request, excel_automation
    EXCEL_AUTOMATION_AVAILABLE = True
    print("📊 Excel Automation System loaded successfully")
except ImportError as e:
    print(f"⚠️ Excel Automation not available: {e}")
    EXCEL_AUTOMATION_AVAILABLE = False

# Import intelligent memory system
try:
    from Backend.IntelligentMemory import store_interaction, record_automation_action
    INTELLIGENT_MEMORY_AVAILABLE = True
    print("🧠 Intelligent Memory System loaded successfully")
except ImportError as e:
    print(f"⚠️ Intelligent Memory not available: {e}")
    INTELLIGENT_MEMORY_AVAILABLE = False

# Import command line automation
try:
    from Backend.CommandLineAutomation import handle_command_line_request
    COMMAND_LINE_AUTOMATION_AVAILABLE = True
    print("🔧 Command Line Automation System loaded successfully")
except ImportError as e:
    print(f"⚠️ Command Line Automation not available: {e}")
    COMMAND_LINE_AUTOMATION_AVAILABLE = False

# Import Gmail automation
try:
    from Backend.GmailIntegration import handle_gmail_request
    GMAIL_AUTOMATION_AVAILABLE = True
    print("📧 Gmail Automation System loaded successfully")
except ImportError as e:
    print(f"⚠️ Gmail Automation not available: {e}")
    GMAIL_AUTOMATION_AVAILABLE = False

env_vars = dotenv_values(".env")  
GroqAPIKey = env_vars.get('GroqAPIKey')

client = Groq(api_key=GroqAPIKey)

def make_conversational_response(error_message: str, action: str = "task") -> str:
    """
    Convert technical error messages into conversational responses.
    """
    error_lower = error_message.lower()
    
    # Common error patterns and their conversational responses
    error_patterns = {
        "failed to open": "I couldn't open that for you",
        "not found": "I couldn't find that on your system",
        "permission denied": "I don't have permission to do that",
        "access denied": "I'm not allowed to access that",
        "file not found": "That file doesn't seem to exist",
        "application not found": "That app isn't installed on your computer",
        "network error": "There seems to be a network issue",
        "connection failed": "I couldn't connect to that service",
        "timeout": "That took too long and timed out",
        "invalid": "That doesn't seem to be valid",
        "error": "Something went wrong with that",
        "exception": "I ran into an issue with that",
        "failed": "I couldn't complete that",
        "not available": "That's not available right now",
        "not supported": "That's not supported on your system"
    }
    
    # Check for specific error patterns
    for pattern, response in error_patterns.items():
        if pattern in error_lower:
            # Add some variety to responses
            variations = [
                f"{response}. Maybe try something else?",
                f"{response}. Is there something else I can help you with?",
                f"{response}. Would you like to try a different approach?",
                f"{response}. Let me know if you need help with something else!"
            ]
            return random.choice(variations)
    
    # Generic conversational responses for unknown errors
    generic_responses = [
        "I'm having trouble with that right now. Can I help you with something else?",
        "That didn't work as expected. Is there another way I can assist you?",
        "I couldn't get that to work. Maybe we could try something different?",
        "Something went wrong there. What else can I help you with today?",
        "I'm not able to do that at the moment. Is there anything else you'd like me to try?"
    ]
    
    return random.choice(generic_responses)

professional_responses = [
    "Your Satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to reach out."
]

SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You are a content writer. You have to write content like letters, reports, articles, applications and anything else that you are asked to do. (Note: For emails, use the Gmail integration instead)."},
]

# Enhanced app configuration dictionary with better mappings
APP_CONFIG = {
    # Desktop Applications
    "spotify": {
        "desktop_paths": [
            r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
            r"C:\Program Files\WindowsApps\SpotifyAB.SpotifyMusic_*\Spotify.exe",
            r"C:\Program Files (x86)\Spotify\Spotify.exe"
        ],
        "web_url": "https://open.spotify.com",
        "protocol": "spotify:",
        "search_url": "https://open.spotify.com/search/"
    },
    "discord": {
        "desktop_paths": [
            r"C:\Users\%USERNAME%\AppData\Local\Discord\app-*\Discord.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe --processStart Discord.exe"
        ],
        "web_url": "https://discord.com/app",
        "protocol": "discord://"
    },
    "chrome": {
        "desktop_paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ],
        "web_url": "https://www.google.com"
    },
    "firefox": {
        "desktop_paths": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ],
        "web_url": "https://www.mozilla.org"
    },
    "edge": {
        "desktop_paths": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        ],
        "web_url": "https://www.microsoft.com/edge"
    },
    "notepad": {
        "desktop_paths": ["notepad.exe"],
        "web_url": None
    },
    "calculator": {
        "desktop_paths": ["calc.exe"],
        "web_url": None
    },
    "paint": {
        "desktop_paths": ["mspaint.exe"],
        "web_url": None
    },
    "word": {
        "desktop_paths": [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            "winword.exe"
        ],
        "web_url": "https://www.office.com/launch/word"
    },
    "excel": {
        "desktop_paths": [
            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
            "excel.exe"
        ],
        "web_url": "https://www.office.com/launch/excel"
    },
    "powerpoint": {
        "desktop_paths": [
            r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
            "powerpnt.exe"
        ],
        "web_url": "https://www.office.com/launch/powerpoint"
    },
    "vscode": {
        "desktop_paths": [
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            "code.exe"
        ],
        "web_url": "https://code.visualstudio.com"
    },
    "steam": {
        "desktop_paths": [
            r"C:\Program Files (x86)\Steam\Steam.exe",
            r"C:\Program Files\Steam\Steam.exe"
        ],
        "web_url": "https://store.steampowered.com"
    },
    "whatsapp": {
        "desktop_paths": [
            r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe"
        ],
        "web_url": "https://web.whatsapp.com"
    },
    "telegram": {
        "desktop_paths": [
            r"C:\Users\%USERNAME%\AppData\Roaming\Telegram Desktop\Telegram.exe"
        ],
        "web_url": "https://web.telegram.org"
    }
}

def open_desktop_app(app_path):
    """Open desktop application with multiple fallback methods"""
    try:
        print(f"Attempting to open: {app_path}")
        
        # Method 1: Try os.startfile (most reliable for Windows)
        try:
            os.startfile(app_path)
            print(f"✅ App opened successfully via os.startfile: {app_path}")
            return True
        except Exception as e:
            print(f"os.startfile failed: {e}")
        
        # Method 2: Try using start command with quotes
        try:
            subprocess.run(f'start "" "{app_path}"', shell=True, check=False)
            print(f"✅ App opened successfully via start command: {app_path}")
            return True
        except Exception as e:
            print(f"Start command failed: {e}")
        
        # Method 3: Try direct subprocess with shell
        try:
            subprocess.Popen([app_path], shell=True)
            print(f"✅ App opened successfully via subprocess: {app_path}")
            return True
        except Exception as e:
            print(f"Subprocess failed: {e}")
        
        # Method 4: Try using PowerShell
        try:
            ps_command = f'Start-Process -FilePath "{app_path}" -WindowStyle Normal'
            subprocess.run(["powershell", "-Command", ps_command], shell=True, check=False)
            print(f"✅ App opened successfully via PowerShell: {app_path}")
            return True
        except Exception as e:
            print(f"PowerShell failed: {e}")
        
        # Method 5: Try using explorer
        try:
            subprocess.run(["explorer", app_path], shell=True, check=False)
            print(f"✅ App opened successfully via explorer: {app_path}")
            return True
        except Exception as e:
            print(f"Explorer failed: {e}")
        
        # Method 6: Try using shell=True with quotes
        try:
            subprocess.Popen(f'"{app_path}"', shell=True)
            print(f"✅ App opened successfully via quoted subprocess: {app_path}")
            return True
        except Exception as e:
            print(f"Quoted subprocess failed: {e}")
        
        print(f"❌ All methods failed to open: {app_path}")
        return False
        
    except Exception as e:
        print(f"Error in open_desktop_app: {e}")
        return False

def find_desktop_app(app_name):
    """Find desktop application executable with enhanced detection"""
    app_name_lower = app_name.lower()
    
    # Common app name mappings
    app_mappings = {
        'vs code': 'code.exe',
        'code': 'code.exe',
        'vscode': 'code.exe',
        'whatsapp': 'WhatsApp.exe',
        'telegram': 'Telegram.exe',
        'discord': 'Discord.exe',
        'chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'edge': 'msedge.exe',
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'paint': 'mspaint.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'powerpoint': 'powerpnt.exe',
        'outlook': 'outlook.exe',
        'spotify': 'Spotify.exe',
        'steam': 'Steam.exe',
        'obs': 'obs64.exe',
        'obs studio': 'obs64.exe',
        'vlc': 'vlc.exe',
        'winrar': 'WinRAR.exe',
        '7zip': '7zFM.exe',
        'adobe': 'Acrobat.exe',
        'acrobat': 'Acrobat.exe',
        'photoshop': 'Photoshop.exe',
        'illustrator': 'Illustrator.exe',
        'premiere': 'Adobe Premiere Pro.exe',
        'after effects': 'AfterFX.exe',
        'blender': 'blender.exe',
        'unity': 'Unity.exe',
        'unreal': 'UnrealEditor.exe',
        'minecraft': 'Minecraft.Windows.exe',
        'epic': 'EpicGamesLauncher.exe',
        'origin': 'Origin.exe',
        'battle.net': 'Battle.net.exe',
        'zoom': 'Zoom.exe',
        'teams': 'Teams.exe',
        'skype': 'Skype.exe',
        'slack': 'Slack.exe',
        'dropbox': 'Dropbox.exe',
        'onedrive': 'OneDrive.exe',
        'google drive': 'GoogleDriveFS.exe',
        'utorrent': 'uTorrent.exe',
        'qbittorrent': 'qBittorrent.exe'
    }
    
    # Check if we have a specific configuration for this app
    if app_name_lower in APP_CONFIG:
        config = APP_CONFIG[app_name_lower]
        for path_template in config["desktop_paths"]:
            # Replace %USERNAME% with actual username
            path = path_template.replace("%USERNAME%", os.getenv("USERNAME", ""))
            
            # Handle wildcards in paths
            if "*" in path:
                import glob
                matches = glob.glob(path)
                if matches:
                    return matches[0]  # Return the first match
            else:
                if os.path.exists(path):
                    return path
    
    # Try mapped app names first
    if app_name_lower in app_mappings:
        mapped_exe = app_mappings[app_name_lower]
        
        # Try to find in PATH first
        try:
            result = subprocess.run(['where', mapped_exe], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        # Try common system paths for mapped apps
        system_paths = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"C:\Users\%s\AppData\Local" % os.getenv("USERNAME", ""),
            r"C:\Users\%s\AppData\Roaming" % os.getenv("USERNAME", ""),
            r"C:\Users\%s\AppData\Local\Programs" % os.getenv("USERNAME", ""),
            r"C:\Users\%s\AppData\Local\Microsoft\WindowsApps" % os.getenv("USERNAME", "")
        ]
        
        for base_path in system_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.lower() == mapped_exe.lower():
                            return os.path.join(root, file)
    
    # Try to find the app using AppOpener as fallback
    try:
        from AppOpener import give_appnames
        available_apps = give_appnames()
        for app in available_apps:
            if app_name_lower in app.lower():
                return app
    except:
        pass
    
    # Try using Windows 'where' command for system apps
    try:
        result = subprocess.run(['where', app_name_lower], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    # Try using Windows 'where' command with .exe extension
    try:
        result = subprocess.run(['where', f"{app_name_lower}.exe"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    # Try common system paths for any matching exe
    system_paths = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\Users\%s\AppData\Local" % os.getenv("USERNAME", ""),
        r"C:\Users\%s\AppData\Roaming" % os.getenv("USERNAME", ""),
        r"C:\Users\%s\AppData\Local\Programs" % os.getenv("USERNAME", ""),
        r"C:\Users\%s\AppData\Local\Microsoft\WindowsApps" % os.getenv("USERNAME", ""),
        r"C:\Users\%s\Desktop" % os.getenv("USERNAME", ""),
        r"C:\Users\%s\Downloads" % os.getenv("USERNAME", ""),
        r"C:\Windows\System32",
        r"C:\Windows"
    ]
    
    for base_path in system_paths:
        if os.path.exists(base_path):
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith('.exe') and app_name_lower in file.lower():
                        return os.path.join(root, file)
    
    # Try partial matching for any exe file
    for base_path in system_paths:
        if os.path.exists(base_path):
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith('.exe'):
                        # Check if any word in app_name is in the filename
                        app_words = app_name_lower.split()
                        file_lower = file.lower()
                        if any(word in file_lower for word in app_words):
                            return os.path.join(root, file)
    
    return None

def open_web_app(app_name, query=None):
    """Open web application"""
    app_name_lower = app_name.lower()
    
    if app_name_lower in APP_CONFIG and APP_CONFIG[app_name_lower]["web_url"]:
        base_url = APP_CONFIG[app_name_lower]["web_url"]
        
        # Handle special cases for music streaming
        if app_name_lower == "spotify" and query:
            # Extract song/artist from query
            search_query = query.replace("play", "").replace("spotify", "").strip()
            if search_query:
                search_url = f"https://open.spotify.com/search/{search_query.replace(' ', '%20')}"
                webbrowser.open(search_url)
                return True
        
        webbrowser.open(base_url)
        return True
    
    # Fallback: search for the app
    search_url = f"https://www.google.com/search?q={app_name}"
    webbrowser.open(search_url)
    return True

def OpenApp(app_command):
    """Enhanced app opening with better error handling and fallbacks"""
    try:
        # Extract app name and any additional query
        parts = app_command.strip().split(" ", 1)
        app_name = parts[0].lower()
        query = parts[1] if len(parts) > 1 else None
        
        # Handle special cases for multi-word app names
        if app_name == "vs" and query and "code" in query.lower():
            app_name = "vs code"
            query = query.replace("code", "").strip()
        elif app_name == "visual" and query and "studio" in query.lower():
            app_name = "visual studio"
            query = query.replace("studio", "").strip()
        elif app_name == "microsoft" and query and "word" in query.lower():
            app_name = "word"
            query = query.replace("word", "").strip()
        elif app_name == "microsoft" and query and "excel" in query.lower():
            app_name = "excel"
            query = query.replace("excel", "").strip()
        elif app_name == "microsoft" and query and "powerpoint" in query.lower():
            app_name = "powerpoint"
            query = query.replace("powerpoint", "").strip()
        
        print(f"Attempting to open: {app_name}")
        if query:
            print(f"With query: {query}")
        
        # Special handling for drives
        if app_name in ["d", "c", "e", "f"] and len(app_name) == 1:
            drive_letter = app_name.upper()
            try:
                drive_path = f"{drive_letter}:\\"
                subprocess.run(["explorer", drive_path], shell=True)
                return f"Opened {drive_letter} drive"
            except Exception as e:
                print(f"Drive command failed: {e}")
                return f"Failed to open {drive_letter} drive"
        
        # Special handling for file explorer
        if app_name in ["file", "explorer", "files"]:
            try:
                subprocess.run(["explorer"], shell=True)
                return "Opened File Explorer"
            except Exception as e:
                print(f"File Explorer command failed: {e}")
                return "Failed to open File Explorer"
        
        # Special handling for camera
        if app_name in ["camera", "webcam"]:
            try:
                subprocess.run(["start", "ms-camera:"], shell=True)
                return "Opened Camera"
            except Exception as e:
                print(f"Camera command failed: {e}")
                return "Failed to open Camera"
        
        # Special handling for system commands and terminals
        if app_name in ["command", "cmd", "command prompt", "terminal", "powershell", "cmd.exe"]:
            try:
                if app_name in ["powershell", "powershell.exe"]:
                    subprocess.run(["powershell"], shell=True)
                    return "Opened PowerShell"
                else:
                    subprocess.run(["cmd"], shell=True)
                    return "Opened Command Prompt"
            except Exception as e:
                print(f"Terminal command failed: {e}")
                return "Failed to open terminal"
        
        # Special handling for task manager
        if app_name in ["task", "task manager", "taskmgr"]:
            try:
                subprocess.run(["taskmgr"], shell=True)
                return "Opened Task Manager"
            except Exception as e:
                print(f"Task Manager command failed: {e}")
                return "Failed to open Task Manager"
        
        # Special handling for control panel
        if app_name in ["control", "control panel", "controlpanel"]:
            try:
                subprocess.run(["control"], shell=True)
                return "Opened Control Panel"
            except Exception as e:
                print(f"Control Panel command failed: {e}")
                return "Failed to open Control Panel"
        
        # Special handling for command palette and run dialog
        if app_name in ["command palette", "run", "run dialog", "win+r"]:
            try:
                subprocess.run(["cmd", "/c", "start", "shell:AppsFolder"], shell=True)
                return "Opened Command Palette"
            except Exception as e:
                print(f"Command Palette command failed: {e}")
                return "Failed to open Command Palette"
        
        # First, try to find and open desktop application
        desktop_path = find_desktop_app(app_name)
        if desktop_path:
            print(f"Found desktop app: {desktop_path}")
            
            # Check if it's a Windows Store app
            if "WindowsApps" in desktop_path:
                print("Detected Windows Store app, using special handling")
                # Extract app name for Windows Store
                app_package_name = desktop_path.split("\\")[-2]  # Get the package name
                if open_windows_store_app(app_package_name):
                    return f"Opened {app_name} Windows Store application"
            else:
                # Regular desktop app
                if open_desktop_app(desktop_path):
                    return f"Opened {app_name} desktop application"
                else:
                    print(f"Failed to open desktop app: {desktop_path}")
                    # Continue to web fallback
        
        # If desktop app not found or failed, try web version
        print(f"Desktop app not found or failed, trying web version")
        if open_web_app(app_name, query):
            return f"Opened {app_name} web application"
        
        # Final fallback: use AppOpener
        try:
            from AppOpener import open as appopen
            appopen(app_name, match_closest=True, output=True, throw_error=True)
            return f"Opened {app_name} using AppOpener"
        except Exception as e:
            print(f"AppOpener failed: {e}")
            
            # Last resort: search on Google
            search_url = f"https://www.google.com/search?q={app_name}"
            webbrowser.open(search_url)
            return f"I couldn't find {app_name} on your system, but I opened a web search for you."
            
    except Exception as e:
        print(f"Error in OpenApp: {e}")
        return f"I couldn't open {app_name}. {make_conversational_response(str(e), 'app')}"
            
def CloseApp(app):
    """Enhanced app closing with better error handling"""
    try:
        app_name = app.lower()
        
        # Special handling for browsers
        if "chrome" in app_name:
            try:
                subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], shell=True, check=False)
                return f"Closed {app_name}"
            except:
                pass
        
        # Try AppOpener first
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return f"Closed {app_name}"
        except Exception as e:
            print(f"AppOpener close failed: {e}")
        
        # Try taskkill as fallback
        try:
            # Map common app names to their process names
            process_mapping = {
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'edge': 'msedge.exe',
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'paint': 'mspaint.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe',
                'powerpoint': 'powerpnt.exe',
                'spotify': 'spotify.exe',
                'discord': 'discord.exe',
                'steam': 'steam.exe',
                'whatsapp': 'whatsapp.exe',
                'telegram': 'telegram.exe',
                'vscode': 'code.exe',
                'code': 'code.exe'
            }
            
            process_name = process_mapping.get(app_name, f"{app_name}.exe")
            subprocess.run(["taskkill", "/f", "/im", process_name], shell=True, check=False)
            return f"Closed {app_name}"
        except Exception as e:
            print(f"Taskkill failed: {e}")
            return f"Could not close {app_name}"
            
    except Exception as e:
        print(f"Error in CloseApp: {e}")
        return f"Failed to close {app}: {str(e)}"

def open_windows_store_app(app_name):
    """Open Windows Store apps using shell commands and PowerShell"""
    try:
        # Method 1: Try using start command with app name
        subprocess.run(["start", app_name], shell=True)
        return True
    except Exception as e:
        print(f"Start command failed: {e}")
        
        try:
            # Method 2: Try using PowerShell to launch Windows Store app
            if "spotify" in app_name.lower():
                # Spotify-specific PowerShell command
                ps_command = r'Start-Process "shell:AppsFolder\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"'
                subprocess.run(["powershell", "-Command", ps_command], shell=True)
                return True
            else:
                # Generic PowerShell command for Windows Store apps
                ps_command = f'Get-AppxPackage | Where-Object {{$_.Name -like "*{app_name}*"}} | ForEach-Object {{Start-Process $_.PackageFamilyName}}'
                subprocess.run(["powershell", "-Command", ps_command], shell=True)
                return True
        except Exception as e2:
            print(f"PowerShell method failed: {e2}")
            
            try:
                # Method 3: Try using shell:AppsFolder
                subprocess.run(["explorer", "shell:AppsFolder"], shell=True)
                return True
            except Exception as e3:
                print(f"AppsFolder method failed: {e3}")
                return False

def open_spotify_specific():
    """Specialized function to open Spotify with multiple methods"""
    try:
        # Method 1: Try using the Spotify protocol
        subprocess.run(["start", "spotify:"], shell=True)
        return True
    except Exception as e:
        print(f"Spotify protocol failed: {e}")
        
        try:
            # Method 2: Try using PowerShell to launch Spotify
            ps_command = r'Start-Process "shell:AppsFolder\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"'
            subprocess.run(["powershell", "-Command", ps_command], shell=True)
            return True
        except Exception as e2:
            print(f"PowerShell Spotify method failed: {e2}")
            
            try:
                # Method 3: Try using the direct executable path with different approach
                spotify_path = r"C:\Program Files\WindowsApps\SpotifyAB.SpotifyMusic_1.270.409.0_x64__zpdnekdrzrea0\Spotify.exe"
                if os.path.exists(spotify_path):
                    # Use shell execution
                    os.system(f'"{spotify_path}"')
                    return True
            except Exception as e3:
                print(f"Direct Spotify path failed: {e3}")
                return False

def spotify_desktop_search(query, skip_search=False):
    """🎯 Smart Spotify Desktop Search and Play with Enhanced Click Detection"""
    try:
        import pyautogui
        import time
        
        print(f"🎯 Starting smart Spotify automation for: {query}")
        
        # Wait for Spotify to be active
        time.sleep(2)
        
        # Try to bring Spotify to front using pyautogui
        try:
            # Find Spotify window and click on it
            spotify_window = pyautogui.getWindowsWithTitle("Spotify")
            if spotify_window:
                spotify_window[0].activate()
                time.sleep(1)
        except:
            pass
        
        # Skip search if already done (e.g., by protocol)
        if not skip_search:
            # Use keyboard shortcuts to search
            # Ctrl+L is the universal Spotify search shortcut
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            
            # Clear any existing text and type new search
            pyautogui.hotkey('ctrl', 'a')  # Select all
            time.sleep(0.2)
            pyautogui.write(query)  # Type the query
            time.sleep(0.5)
            pyautogui.press('enter')  # Search
            
            # Wait for search results to load
            time.sleep(3)
        else:
                print("🔄 Skipping search (already done by protocol)")
                # Just wait a bit for the search results to be ready
                time.sleep(2)
        
        # 🎯 SMART CLICK DETECTION AND PLAYBACK
        print("🎯 Detecting and clicking first search result...")
        
        # Method 1: Smart keyboard navigation (most reliable)
        try:
            # Press Tab to move focus to search results
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Press Down arrow to select first result
            pyautogui.press('down')
            time.sleep(0.5)
            
            # Press Enter to play the selected result
            pyautogui.press('enter')
            time.sleep(1)
            
            # Additional play attempts to ensure it starts
            pyautogui.press('space')  # Try spacebar to play
            time.sleep(0.5)
            pyautogui.press('enter')  # Try enter again
            time.sleep(0.5)
            
            # Try clicking on the first result area as backup
            spotify_windows = pyautogui.getWindowsWithTitle("Spotify")
            if spotify_windows:
                window = spotify_windows[0]
                # Click in the area where first result typically appears
                pyautogui.click(window.left + (window.width // 3), window.top + (window.height // 3))
                time.sleep(0.5)
                pyautogui.press('enter')
            
            print("✅ Smart keyboard navigation completed!")
            return True
            
        except Exception as e:
            print(f"⚠️ Keyboard navigation failed: {e}")
        
        # Method 2: Enhanced window-based clicking
        try:
            print("🎯 Using enhanced window-based clicking...")
            
            # Get Spotify window position and size
            spotify_windows = pyautogui.getWindowsWithTitle("Spotify")
            if spotify_windows:
                window = spotify_windows[0]
                
                # Calculate multiple click positions where first result might be
                click_positions = [
                    # Position 1: Center-left area (most common)
                    (window.left + (window.width // 4), window.top + (window.height // 3)),
                    # Position 2: Slightly right of center
                    (window.left + (window.width // 3), window.top + (window.height // 3)),
                    # Position 3: Center area
                    (window.left + (window.width // 2), window.top + (window.height // 3)),
                    # Position 4: Lower area (if results are below)
                    (window.left + (window.width // 3), window.top + (window.height // 2)),
                ]
                
                for i, (x, y) in enumerate(click_positions, 1):
                    print(f"🎯 Trying click position {i}: ({x}, {y})")
                    
                    # Click on the position
                    pyautogui.click(x, y)
                    time.sleep(0.5)
                    
                    # Try to play with spacebar
                    pyautogui.press('space')
                    time.sleep(0.5)
                    
                    # Try double-click as well
                    pyautogui.doubleClick(x, y)
                    time.sleep(0.5)
                    
                    # Try Enter key
                    pyautogui.press('enter')
                    time.sleep(0.5)
                    
                    print(f"✅ Click position {i} attempted")
                
                print("✅ Enhanced window-based clicking completed!")
                return True
                
        except Exception as e:
            print(f"⚠️ Window-based clicking failed: {e}")
        
        # Method 3: AI Vision Enhancement (if available)
        if SCREEN_VISION_AVAILABLE:
            try:
                print("🖥️ Using AI vision for precise click detection...")
                
                # Capture and analyze current screen
                analysis = capture_and_analyze(f"spotify search results for {query}")
                print(f"📊 AI Analysis:\n{analysis}")
                
                # Get smart click position for first search result
                click_pos = get_smart_click_position("first search result in spotify")
                
                if click_pos:
                    x, y = click_pos
                    print(f"🎯 AI detected optimal click position: ({x}, {y})")
                    
                    # Click on the detected position
                    pyautogui.click(x=x, y=y)
                    time.sleep(0.5)
                    
                    # Double-click to play
                    pyautogui.doubleClick(x=x, y=y)
                    time.sleep(0.5)
                    
                    # Try spacebar as well
                    pyautogui.press('space')
                    time.sleep(0.5)
                    
                    print("✅ AI vision-guided click completed successfully!")
                    return True
                else:
                    print("⚠️ AI couldn't detect optimal click position")
                
            except Exception as e:
                print(f"⚠️ AI vision failed: {e}")
        
        # Method 4: Fallback - Try multiple keyboard shortcuts
        try:
            print("🔄 Using fallback keyboard shortcuts...")
            
            # Try various Spotify shortcuts
            shortcuts = [
                ('space', 'Play/Pause'),
                ('enter', 'Enter'),
                ('ctrl', 'shift', 'right', 'Next track'),
                ('ctrl', 'shift', 'left', 'Previous track'),
                ('ctrl', 'up', 'Volume up'),
                ('ctrl', 'down', 'Volume down'),
            ]
            
            for shortcut in shortcuts:
                try:
                    if len(shortcut) == 1:
                        pyautogui.press(shortcut[0])
                    else:
                        pyautogui.hotkey(*shortcut[:-1])  # Exclude the description
                    time.sleep(0.3)
                    print(f"✅ Tried shortcut: {shortcut[-1]}")
                except:
                    continue
            
            print("✅ Fallback shortcuts completed!")
            return True
            
        except Exception as e:
            print(f"⚠️ Fallback shortcuts failed: {e}")
        
        # Final fallback: Force play the first result
        try:
            print("🔄 Final fallback: Force playing first result...")
            
            # Get Spotify window
            spotify_windows = pyautogui.getWindowsWithTitle("Spotify")
            if spotify_windows:
                window = spotify_windows[0]
                
                # Click multiple positions where the first result might be
                first_result_positions = [
                    (window.left + (window.width // 3), window.top + (window.height // 3)),
                    (window.left + (window.width // 2), window.top + (window.height // 3)),
                    (window.left + (window.width // 4), window.top + (window.height // 3)),
                    (window.left + (window.width // 3), window.top + (window.height // 2)),
                ]
                
                for i, (x, y) in enumerate(first_result_positions, 1):
                    print(f"🎯 Final attempt {i}: Clicking at ({x}, {y})")
                    pyautogui.click(x, y)
                    time.sleep(0.3)
                    pyautogui.press('enter')
                    time.sleep(0.3)
                    pyautogui.press('space')
                    time.sleep(0.3)
                
                print("✅ Final fallback completed!")
        except Exception as e:
            print(f"⚠️ Final fallback failed: {e}")
        
        print("✅ All automation methods attempted")
        return True
        
    except Exception as e:
        print(f"❌ Spotify automation failed: {e}")
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
    """Enhanced system automation with comprehensive commands"""
    
    def mute():
        keyboard.press_and_release("volume mute")
        
    def unmute():
        keyboard.press_and_release("volume mute")
        
    def volume_up():
        keyboard.press_and_release("volume up")
        
    def volume_down():
        keyboard.press_and_release("volume down")
        
    def sleep_laptop():
        """Put laptop to sleep"""
        try:
            subprocess.run(["powercfg", "/hibernate", "off"], shell=True)
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], shell=True)
            return "Putting laptop to sleep..."
        except Exception as e:
            print(f"Sleep command failed: {e}")
            return "Failed to put laptop to sleep"
    
    def open_camera():
        """Open Windows Camera app"""
        try:
            subprocess.run(["start", "ms-camera:"], shell=True)
            return "Opening camera..."
        except Exception as e:
            print(f"Camera command failed: {e}")
            return "Failed to open camera"
    
    def open_drive(drive_letter):
        """Open specific drive in File Explorer"""
        try:
            drive_path = f"{drive_letter}:\\"
            subprocess.run(["explorer", drive_path], shell=True)
            return f"Opening {drive_letter} drive..."
        except Exception as e:
            print(f"Drive command failed: {e}")
            return f"Failed to open {drive_letter} drive"
    
    def search_files(query):
        """Search for files/folders using Windows Search"""
        try:
            # Open Windows Search
            keyboard.press_and_release("windows")
            time.sleep(0.5)
            keyboard.write(query)
            time.sleep(0.5)
            keyboard.press_and_release("enter")
            return f"Searching for: {query}"
        except Exception as e:
            print(f"Search command failed: {e}")
            return f"Failed to search for: {query}"
    
    def open_file_explorer():
        """Open File Explorer"""
        try:
            subprocess.run(["explorer"], shell=True)
            return "Opening File Explorer..."
        except Exception as e:
            print(f"File Explorer command failed: {e}")
            return "Failed to open File Explorer"
    
    def open_file_explorer_at_path(path):
        """Open File Explorer at specific path"""
        try:
            subprocess.run(["explorer", path], shell=True)
            return f"Opening File Explorer at: {path}"
        except Exception as e:
            print(f"File Explorer path command failed: {e}")
            return f"Failed to open File Explorer at: {path}"
    
    def create_folder_with_explorer(folder_name):
        """Create a folder using File Explorer automation"""
        try:
            import pyautogui
            import time
            
            # Open File Explorer
            subprocess.run(["explorer"], shell=True)
            time.sleep(2)
            
            # Use keyboard shortcut to create new folder
            pyautogui.hotkey('ctrl', 'shift', 'n')  # Windows shortcut for new folder
            time.sleep(1)
            
            # Type the folder name
            pyautogui.write(folder_name)
            time.sleep(0.5)
            pyautogui.press('enter')
            
            return f"✅ Created folder '{folder_name}' using File Explorer"
        except Exception as e:
            print(f"File Explorer folder creation failed: {e}")
            return f"Failed to create folder '{folder_name}' using File Explorer"
    
    def create_file_with_explorer(file_name):
        """Create a file using File Explorer automation"""
        try:
            import pyautogui
            import time
            
            # Open File Explorer
            subprocess.run(["explorer"], shell=True)
            time.sleep(2)
            
            # Right-click to open context menu
            pyautogui.rightClick()
            time.sleep(0.5)
            
            # Navigate to New -> Text Document
            pyautogui.press('w')  # Press 'w' for "New"
            time.sleep(0.5)
            pyautogui.press('t')  # Press 't' for "Text Document"
            time.sleep(1)
            
            # Type the file name
            pyautogui.write(file_name)
            time.sleep(0.5)
            pyautogui.press('enter')
            
            return f"✅ Created file '{file_name}' using File Explorer"
        except Exception as e:
            print(f"File Explorer file creation failed: {e}")
            return f"Failed to create file '{file_name}' using File Explorer"
    
    def open_notepad():
        """Open Notepad"""
        try:
            subprocess.run(["notepad"], shell=True)
            return "Opening Notepad..."
        except Exception as e:
            print(f"Notepad command failed: {e}")
            return "Failed to open Notepad"
    
    def open_calculator():
        """Open Calculator"""
        try:
            subprocess.run(["calc"], shell=True)
            return "Opening Calculator..."
        except Exception as e:
            print(f"Calculator command failed: {e}")
            return "Failed to open Calculator"
    
    def open_paint():
        """Open Paint"""
        try:
            subprocess.run(["mspaint"], shell=True)
            return "Opening Paint..."
        except Exception as e:
            print(f"Paint command failed: {e}")
            return "Failed to open Paint"
    
    def take_screenshot():
        """Take a screenshot"""
        try:
            keyboard.press_and_release("windows+shift+s")
            return "Taking screenshot..."
        except Exception as e:
            print(f"Screenshot command failed: {e}")
            return "Failed to take screenshot"
    
    def lock_computer():
        """Lock the computer"""
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], shell=True)
            return "Locking computer..."
        except Exception as e:
            print(f"Lock command failed: {e}")
            return "Failed to lock computer"
    
    def restart_computer():
        """Restart the computer"""
        try:
            subprocess.run(["shutdown", "/r", "/t", "0"], shell=True)
            return "Restarting computer..."
        except Exception as e:
            print(f"Restart command failed: {e}")
            return "Failed to restart computer"
    
    def shutdown_computer():
        """Shutdown the computer"""
        try:
            subprocess.run(["shutdown", "/s", "/t", "0"], shell=True)
            return "Shutting down computer..."
        except Exception as e:
            print(f"Shutdown command failed: {e}")
            return "Failed to shutdown computer"
    
    # Command processing
    command_lower = command.lower()
    
    if command == "mute":
        mute()
        return "Muted audio"
    elif command == "unmute":
        unmute()
        return "Unmuted audio"
    elif command == "volume up":
        volume_up()
        return "Volume increased"
    elif command == "volume down":
        volume_down()
        return "Volume decreased"
    elif "sleep" in command_lower or "laptop to sleep" in command_lower:
        return sleep_laptop()
    elif "camera" in command_lower:
        return open_camera()
    elif "d drive" in command_lower or "d:" in command_lower:
        return open_drive("D")
    elif "c drive" in command_lower or "c:" in command_lower:
        return open_drive("C")
    elif "file explorer" in command_lower or "explorer" in command_lower:
        return open_file_explorer()
    elif "notepad" in command_lower:
        return open_notepad()
    elif "calculator" in command_lower or "calc" in command_lower:
        return open_calculator()
    elif "paint" in command_lower:
        return open_paint()
    elif "screenshot" in command_lower:
        return take_screenshot()
    elif "lock" in command_lower:
        return lock_computer()
    elif "restart" in command_lower:
        return restart_computer()
    elif "shutdown" in command_lower or "shut down" in command_lower:
        return shutdown_computer()
    elif "search" in command_lower:
        # Extract search query
        search_query = command_lower.replace("search", "").replace("for", "").strip()
        if search_query:
            return search_files(search_query)
        else:
            return "Please specify what to search for"
    elif "analyze screen" in command_lower or "see screen" in command_lower:
        if SCREEN_VISION_AVAILABLE:
            analysis = capture_and_analyze("analyze current screen")
            print(f"🖥️ Screen Analysis: {analysis}")
            return f"Screen analyzed: {analysis[:100]}..."
        else:
            return "Screen vision not available"
    elif "screen monitoring" in command_lower or "monitor screen" in command_lower:
        if SCREEN_VISION_AVAILABLE:
            start_screen_monitoring()
            return "Screen monitoring started"
        else:
            return "Screen vision not available"
        # 🎮 Gaming & Entertainment
    elif "steam" in command_lower:
        return open_steam()
    elif "epic games" in command_lower or "epic" in command_lower:
        return open_epic_games()
    elif "discord" in command_lower:
        return open_discord()
    elif "netflix" in command_lower:
        return open_netflix()
    elif "youtube" in command_lower and "app" in command_lower:
        return open_youtube_app()
    
    # 📱 Communication & Social
    elif "whatsapp" in command_lower:
        return open_whatsapp()
    elif "telegram" in command_lower:
        return open_telegram()
    elif "teams" in command_lower or "microsoft teams" in command_lower:
        return open_teams()
    elif "zoom" in command_lower:
        return open_zoom()
    elif "skype" in command_lower:
        return open_skype()
    
    # 💼 Productivity & Office
    elif "word" in command_lower or "microsoft word" in command_lower:
        return open_word()
    elif "excel" in command_lower or "microsoft excel" in command_lower:
        return open_excel()
    elif "powerpoint" in command_lower or "microsoft powerpoint" in command_lower:
        return open_powerpoint()
    elif "outlook" in command_lower or "microsoft outlook" in command_lower:
        return open_outlook()
    elif "chrome" in command_lower:
        return open_chrome()
    elif "firefox" in command_lower:
        return open_firefox()
    elif "edge" in command_lower or "microsoft edge" in command_lower:
        return open_edge()
    
    # 🎨 Creative & Design
    elif "photoshop" in command_lower or "adobe photoshop" in command_lower:
        return open_photoshop()
    elif "illustrator" in command_lower or "adobe illustrator" in command_lower:
        return open_illustrator()
    elif "premiere" in command_lower or "adobe premiere" in command_lower:
        return open_premiere()
    elif "blender" in command_lower:
        return open_blender()
    elif "obs" in command_lower or "obs studio" in command_lower:
        return open_obs()
    
    # 🔧 Development & Programming
    elif "visual studio" in command_lower or "vs code" in command_lower:
        return open_vscode()
    elif "pycharm" in command_lower:
        return open_pycharm()
    elif "intellij" in command_lower:
        return open_intellij()
    elif "git" in command_lower and "bash" in command_lower:
        return open_gitbash()
    elif "terminal" in command_lower or "cmd" in command_lower:
        return open_terminal()
    elif "powershell" in command_lower:
        return open_powershell()
    
    # 📊 System & Utilities
    elif "task manager" in command_lower:
        return open_task_manager()
    elif "control panel" in command_lower:
        return open_control_panel()
    elif "settings" in command_lower or "windows settings" in command_lower:
        return open_settings()
    elif "device manager" in command_lower:
        return open_device_manager()
    elif "disk cleanup" in command_lower:
        return run_disk_cleanup()
    elif "defragment" in command_lower or "defrag" in command_lower:
        return run_defrag()
    
    # 🎵 Media & Audio
    elif "vlc" in command_lower:
        return open_vlc()
    elif "windows media player" in command_lower:
        return open_windows_media_player()
    elif "groove music" in command_lower:
        return open_groove_music()
    elif "audacity" in command_lower:
        return open_audacity()
    
    # 📁 File Operations
    elif "desktop" in command_lower:
        return open_desktop()
    elif "documents" in command_lower:
        return open_documents()
    elif "downloads" in command_lower:
        return open_downloads()
    elif "pictures" in command_lower:
        return open_pictures()
    elif "videos" in command_lower:
        return open_videos()
    elif "music folder" in command_lower:
        return open_music_folder()
    
    # 🔒 Security & Privacy
    elif "windows defender" in command_lower:
        return open_windows_defender()
    elif "firewall" in command_lower:
        return open_firewall()
    elif "bitlocker" in command_lower:
        return open_bitlocker()
    
    # 🌐 Network & Internet
    elif "network settings" in command_lower:
        return open_network_settings()
    elif "wifi settings" in command_lower:
        return open_wifi_settings()
    elif "ethernet" in command_lower:
        return open_ethernet_settings()
    
    # 🎯 Advanced Automation
    elif "clean desktop" in command_lower:
        return clean_desktop()
    elif "organize files" in command_lower:
        return organize_files()
    elif "backup files" in command_lower:
        return backup_files()
    elif "system info" in command_lower:
        return get_system_info()
    elif "battery status" in command_lower:
        return get_battery_status()
    elif "memory usage" in command_lower:
        return get_memory_usage()
    elif "cpu usage" in command_lower:
        return get_cpu_usage()
    elif "disk space" in command_lower:
        return get_disk_space()
    
    else:
        return f"Unknown system command: {command}"
        
    return True


async def TranslateAndExecute(commands: list[str]):
    funcs = []
    processed_commands = set()  # Track processed commands to avoid duplicates
    
    # Pre-process commands to detect Spotify + song combinations
    open_spotify_cmd = None
    play_song_cmd = None
    
    for command in commands:
        command_lower = command.lower()
        if command.startswith("open spotify"):
            open_spotify_cmd = command
        elif command.startswith("play "):
            play_song_cmd = command
    
    # If we have both open spotify and play commands, combine them
    if open_spotify_cmd and play_song_cmd:
        song_name = play_song_cmd.removeprefix("play ").strip()
        spotify_song = f"spotify {song_name}"
        # Add the combined command and mark both as processed
        fun = asyncio.to_thread(PlayMusic, spotify_song)
        funcs.append(fun)
        processed_commands.add(open_spotify_cmd)
        processed_commands.add(play_song_cmd)
        print(f"Combined Spotify command: {spotify_song}")
    
    for command in commands:
        command_lower = command.lower()
        
        # Skip if already processed
        if command in processed_commands:
            continue
        
        if command.startswith("open "): 
            
            if "open it" in command: 
                pass
            
            if "open file" in command: 
                pass
            
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open ")) 
                funcs.append(fun)
                processed_commands.add(command)
                
        elif command.startswith("general "): 
            pass
            
        elif command.startswith("realtime "): 
            pass
            
        elif command.startswith("close "): 
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close ")) 
            funcs.append(fun)
            processed_commands.add(command)
            
        elif command.startswith("play "):
            # Use the enhanced PlayMusic function for better music handling
            fun = asyncio.to_thread(PlayMusic, command.removeprefix("play ")) 
            funcs.append(fun)
            processed_commands.add(command)
            
        elif command.startswith("content "): 
            fun = asyncio.to_thread(Content, command.removeprefix("content ")) 
            funcs.append(fun)
            processed_commands.add(command)
            
        elif command.startswith("google search "): 
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")) 
            funcs.append(fun)
            processed_commands.add(command)
            
        elif command.startswith("youtube search "): 
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")) 
            funcs.append(fun)
            processed_commands.add(command)
            
        elif command.startswith("search "): 
            fun = asyncio.to_thread(System, f"search {command.removeprefix('search ')}") 
            funcs.append(fun)
            processed_commands.add(command)
            
        elif command.startswith("system "): 
            fun = asyncio.to_thread(System, command.removeprefix("system ")) 
            funcs.append(fun)
            processed_commands.add(command)
            
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

# 🎮 Gaming & Entertainment Functions
def open_steam():
    """Open Steam gaming platform"""
    try:
        subprocess.run(["start", "steam://"], shell=True)
        return "Opening Steam..."
    except Exception as e:
        return f"Failed to open Steam: {e}"

def open_epic_games():
    """Open Epic Games Launcher"""
    try:
        subprocess.run(["start", "com.epicgames.launcher://"], shell=True)
        return "Opening Epic Games..."
    except Exception as e:
        return f"Failed to open Epic Games: {e}"

def open_discord():
    """Open Discord"""
    try:
        subprocess.run(["start", "discord://"], shell=True)
        return "Opening Discord..."
    except Exception as e:
        return f"Failed to open Discord: {e}"

def open_netflix():
    """Open Netflix"""
    try:
        subprocess.run(["start", "netflix://"], shell=True)
        return "Opening Netflix..."
    except Exception as e:
        return f"Failed to open Netflix: {e}"

def open_youtube_app():
    """Open YouTube app"""
    try:
        subprocess.run(["start", "youtube://"], shell=True)
        return "Opening YouTube app..."
    except Exception as e:
        return f"Failed to open YouTube app: {e}"

# 📱 Communication & Social Functions
def open_whatsapp():
    """Open WhatsApp"""
    try:
        subprocess.run(["start", "whatsapp://"], shell=True)
        return "Opening WhatsApp..."
    except Exception as e:
        return f"Failed to open WhatsApp: {e}"

def open_telegram():
    """Open Telegram"""
    try:
        subprocess.run(["start", "telegram://"], shell=True)
        return "Opening Telegram..."
    except Exception as e:
        return f"Failed to open Telegram: {e}"

def open_teams():
    """Open Microsoft Teams"""
    try:
        subprocess.run(["start", "msteams://"], shell=True)
        return "Opening Microsoft Teams..."
    except Exception as e:
        return f"Failed to open Teams: {e}"

def open_zoom():
    """Open Zoom"""
    try:
        subprocess.run(["start", "zoommtg://"], shell=True)
        return "Opening Zoom..."
    except Exception as e:
        return f"Failed to open Zoom: {e}"

def open_skype():
    """Open Skype"""
    try:
        subprocess.run(["start", "skype://"], shell=True)
        return "Opening Skype..."
    except Exception as e:
        return f"Failed to open Skype: {e}"

# 💼 Productivity & Office Functions
def open_word():
    """Open Microsoft Word"""
    try:
        subprocess.run(["start", "winword"], shell=True)
        return "Opening Microsoft Word..."
    except Exception as e:
        return f"Failed to open Word: {e}"

def open_excel():
    """Open Microsoft Excel"""
    try:
        subprocess.run(["start", "excel"], shell=True)
        return "Opening Microsoft Excel..."
    except Exception as e:
        return f"Failed to open Excel: {e}"

def open_powerpoint():
    """Open Microsoft PowerPoint"""
    try:
        subprocess.run(["start", "powerpnt"], shell=True)
        return "Opening Microsoft PowerPoint..."
    except Exception as e:
        return f"Failed to open PowerPoint: {e}"

def open_outlook():
    """Open Microsoft Outlook"""
    try:
        subprocess.run(["start", "outlook"], shell=True)
        return "Opening Microsoft Outlook..."
    except Exception as e:
        return f"Failed to open Outlook: {e}"

def open_chrome():
    """Open Google Chrome"""
    try:
        subprocess.run(["start", "chrome"], shell=True)
        return "Opening Google Chrome..."
    except Exception as e:
        return f"Failed to open Chrome: {e}"

def open_firefox():
    """Open Mozilla Firefox"""
    try:
        subprocess.run(["start", "firefox"], shell=True)
        return "Opening Mozilla Firefox..."
    except Exception as e:
        return f"Failed to open Firefox: {e}"

def open_edge():
    """Open Microsoft Edge"""
    try:
        subprocess.run(["start", "msedge"], shell=True)
        return "Opening Microsoft Edge..."
    except Exception as e:
        return f"Failed to open Edge: {e}"

# 🎨 Creative & Design Functions
def open_photoshop():
    """Open Adobe Photoshop"""
    try:
        subprocess.run(["start", "photoshop"], shell=True)
        return "Opening Adobe Photoshop..."
    except Exception as e:
        return f"Failed to open Photoshop: {e}"

def open_illustrator():
    """Open Adobe Illustrator"""
    try:
        subprocess.run(["start", "illustrator"], shell=True)
        return "Opening Adobe Illustrator..."
    except Exception as e:
        return f"Failed to open Illustrator: {e}"

def open_premiere():
    """Open Adobe Premiere Pro"""
    try:
        subprocess.run(["start", "premiere"], shell=True)
        return "Opening Adobe Premiere Pro..."
    except Exception as e:
        return f"Failed to open Premiere: {e}"

def open_blender():
    """Open Blender"""
    try:
        subprocess.run(["start", "blender"], shell=True)
        return "Opening Blender..."
    except Exception as e:
        return f"Failed to open Blender: {e}"

def open_obs():
    """Open OBS Studio"""
    try:
        subprocess.run(["start", "obs64"], shell=True)
        return "Opening OBS Studio..."
    except Exception as e:
        return f"Failed to open OBS: {e}"

# 🔧 Development & Programming Functions
def open_vscode():
    """Open Visual Studio Code"""
    try:
        subprocess.run(["start", "code"], shell=True)
        return "Opening Visual Studio Code..."
    except Exception as e:
        return f"Failed to open VS Code: {e}"

def open_pycharm():
    """Open PyCharm"""
    try:
        subprocess.run(["start", "pycharm64"], shell=True)
        return "Opening PyCharm..."
    except Exception as e:
        return f"Failed to open PyCharm: {e}"

def open_intellij():
    """Open IntelliJ IDEA"""
    try:
        subprocess.run(["start", "idea64"], shell=True)
        return "Opening IntelliJ IDEA..."
    except Exception as e:
        return f"Failed to open IntelliJ: {e}"

def open_gitbash():
    """Open Git Bash"""
    try:
        subprocess.run(["start", "git-bash"], shell=True)
        return "Opening Git Bash..."
    except Exception as e:
        return f"Failed to open Git Bash: {e}"

def open_terminal():
    """Open Command Prompt"""
    try:
        subprocess.run(["start", "cmd"], shell=True)
        return "Opening Command Prompt..."
    except Exception as e:
        return f"Failed to open Terminal: {e}"

def open_powershell():
    """Open PowerShell"""
    try:
        subprocess.run(["start", "powershell"], shell=True)
        return "Opening PowerShell..."
    except Exception as e:
        return f"Failed to open PowerShell: {e}"

# 📊 System & Utilities Functions
def open_task_manager():
    """Open Task Manager"""
    try:
        subprocess.run(["start", "taskmgr"], shell=True)
        return "Opening Task Manager..."
    except Exception as e:
        return f"Failed to open Task Manager: {e}"

def open_control_panel():
    """Open Control Panel"""
    try:
        subprocess.run(["start", "control"], shell=True)
        return "Opening Control Panel..."
    except Exception as e:
        return f"Failed to open Control Panel: {e}"

def open_settings():
    """Open Windows Settings"""
    try:
        subprocess.run(["start", "ms-settings:"], shell=True)
        return "Opening Windows Settings..."
    except Exception as e:
        return f"Failed to open Settings: {e}"

def open_device_manager():
    """Open Device Manager"""
    try:
        subprocess.run(["start", "devmgmt.msc"], shell=True)
        return "Opening Device Manager..."
    except Exception as e:
        return f"Failed to open Device Manager: {e}"

def run_disk_cleanup():
    """Run Disk Cleanup"""
    try:
        subprocess.run(["start", "cleanmgr"], shell=True)
        return "Running Disk Cleanup..."
    except Exception as e:
        return f"Failed to run Disk Cleanup: {e}"

def run_defrag():
    """Run Disk Defragmenter"""
    try:
        subprocess.run(["start", "dfrgui"], shell=True)
        return "Running Disk Defragmenter..."
    except Exception as e:
        return f"Failed to run Defrag: {e}"

# 🎵 Media & Audio Functions
def open_vlc():
    """Open VLC Media Player"""
    try:
        subprocess.run(["start", "vlc"], shell=True)
        return "Opening VLC Media Player..."
    except Exception as e:
        return f"Failed to open VLC: {e}"

def open_windows_media_player():
    """Open Windows Media Player"""
    try:
        subprocess.run(["start", "wmplayer"], shell=True)
        return "Opening Windows Media Player..."
    except Exception as e:
        return f"Failed to open Windows Media Player: {e}"

def open_groove_music():
    """Open Groove Music"""
    try:
        subprocess.run(["start", "ms-windows-store://pdp/?ProductId=9WZDNCRFJ3PT"], shell=True)
        return "Opening Groove Music..."
    except Exception as e:
        return f"Failed to open Groove Music: {e}"

def open_audacity():
    """Open Audacity"""
    try:
        subprocess.run(["start", "audacity"], shell=True)
        return "Opening Audacity..."
    except Exception as e:
        return f"Failed to open Audacity: {e}"

# 📁 File Operations Functions
def open_desktop():
    """Open Desktop folder"""
    try:
        subprocess.run(["explorer", os.path.expanduser("~/Desktop")], shell=True)
        return "Opening Desktop folder..."
    except Exception as e:
        return f"Failed to open Desktop: {e}"

def open_documents():
    """Open Documents folder"""
    try:
        subprocess.run(["explorer", os.path.expanduser("~/Documents")], shell=True)
        return "Opening Documents folder..."
    except Exception as e:
        return f"Failed to open Documents: {e}"

def open_downloads():
    """Open Downloads folder"""
    try:
        subprocess.run(["explorer", os.path.expanduser("~/Downloads")], shell=True)
        return "Opening Downloads folder..."
    except Exception as e:
        return f"Failed to open Downloads: {e}"

def open_pictures():
    """Open Pictures folder"""
    try:
        subprocess.run(["explorer", os.path.expanduser("~/Pictures")], shell=True)
        return "Opening Pictures folder..."
    except Exception as e:
        return f"Failed to open Pictures: {e}"

def open_videos():
    """Open Videos folder"""
    try:
        subprocess.run(["explorer", os.path.expanduser("~/Videos")], shell=True)
        return "Opening Videos folder..."
    except Exception as e:
        return f"Failed to open Videos: {e}"

def open_music_folder():
    """Open Music folder"""
    try:
        subprocess.run(["explorer", os.path.expanduser("~/Music")], shell=True)
        return "Opening Music folder..."
    except Exception as e:
        return f"Failed to open Music folder: {e}"

# 🔒 Security & Privacy Functions
def open_windows_defender():
    """Open Windows Defender"""
    try:
        subprocess.run(["start", "windowsdefender://"], shell=True)
        return "Opening Windows Defender..."
    except Exception as e:
        return f"Failed to open Windows Defender: {e}"

def open_firewall():
    """Open Windows Firewall"""
    try:
        subprocess.run(["start", "wf.msc"], shell=True)
        return "Opening Windows Firewall..."
    except Exception as e:
        return f"Failed to open Firewall: {e}"

def open_bitlocker():
    """Open BitLocker Drive Encryption"""
    try:
        subprocess.run(["start", "bitlockerwizard"], shell=True)
        return "Opening BitLocker..."
    except Exception as e:
        return f"Failed to open BitLocker: {e}"

# 🌐 Network & Internet Functions
def open_network_settings():
    """Open Network Settings"""
    try:
        subprocess.run(["start", "ms-settings:network"], shell=True)
        return "Opening Network Settings..."
    except Exception as e:
        return f"Failed to open Network Settings: {e}"

def open_wifi_settings():
    """Open WiFi Settings"""
    try:
        subprocess.run(["start", "ms-settings:network-wifi"], shell=True)
        return "Opening WiFi Settings..."
    except Exception as e:
        return f"Failed to open WiFi Settings: {e}"

def open_ethernet_settings():
    """Open Ethernet Settings"""
    try:
        subprocess.run(["start", "ms-settings:network-ethernet"], shell=True)
        return "Opening Ethernet Settings..."
    except Exception as e:
        return f"Failed to open Ethernet Settings: {e}"

# 🎯 Advanced Automation Functions
def clean_desktop():
    """Clean desktop by organizing files"""
    try:
        desktop_path = os.path.expanduser("~/Desktop")
        # Create folders for organization
        folders = ["Documents", "Pictures", "Videos", "Music", "Downloads", "Other"]
        for folder in folders:
            folder_path = os.path.join(desktop_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        
        # Move files to appropriate folders (basic implementation)
        for file in os.listdir(desktop_path):
            file_path = os.path.join(desktop_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    shutil.move(file_path, os.path.join(desktop_path, "Pictures", file))
                elif ext in ['.mp4', '.avi', '.mov', '.wmv']:
                    shutil.move(file_path, os.path.join(desktop_path, "Videos", file))
                elif ext in ['.mp3', '.wav', '.flac']:
                    shutil.move(file_path, os.path.join(desktop_path, "Music", file))
                elif ext in ['.pdf', '.doc', '.docx', '.txt']:
                    shutil.move(file_path, os.path.join(desktop_path, "Documents", file))
        
        return "Desktop cleaned and organized!"
    except Exception as e:
        return f"Failed to clean desktop: {e}"

def organize_files():
    """Organize files in current directory"""
    try:
        current_dir = os.getcwd()
        # Create folders for organization
        folders = ["Documents", "Pictures", "Videos", "Music", "Archives", "Other"]
        for folder in folders:
            folder_path = os.path.join(current_dir, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        
        # Move files to appropriate folders
        for file in os.listdir(current_dir):
            file_path = os.path.join(current_dir, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    shutil.move(file_path, os.path.join(current_dir, "Pictures", file))
                elif ext in ['.mp4', '.avi', '.mov', '.wmv']:
                    shutil.move(file_path, os.path.join(current_dir, "Videos", file))
                elif ext in ['.mp3', '.wav', '.flac']:
                    shutil.move(file_path, os.path.join(current_dir, "Music", file))
                elif ext in ['.pdf', '.doc', '.docx', '.txt']:
                    shutil.move(file_path, os.path.join(current_dir, "Documents", file))
                elif ext in ['.zip', '.rar', '.7z']:
                    shutil.move(file_path, os.path.join(current_dir, "Archives", file))
        
        return "Files organized successfully!"
    except Exception as e:
        return f"Failed to organize files: {e}"

def backup_files():
    """Create backup of important folders"""
    try:
        import datetime
        backup_dir = os.path.expanduser(f"~/Backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup important folders
        folders_to_backup = ["Documents", "Pictures", "Downloads"]
        for folder in folders_to_backup:
            source = os.path.expanduser(f"~/{folder}")
            if os.path.exists(source):
                dest = os.path.join(backup_dir, folder)
                shutil.copytree(source, dest)
        
        return f"Backup created at: {backup_dir}"
    except Exception as e:
        return f"Failed to create backup: {e}"

def get_system_info():
    """Get system information"""
    try:
        import platform
        import psutil
        
        info = f"""
🖥️ **System Information**
**OS**: {platform.system()} {platform.release()}
**Architecture**: {platform.architecture()[0]}
**Processor**: {platform.processor()}
**Memory**: {psutil.virtual_memory().total // (1024**3)} GB Total
**Available Memory**: {psutil.virtual_memory().available // (1024**3)} GB
**Disk Usage**: {psutil.disk_usage('/').percent}% Used
        """
        return info
    except Exception as e:
        return f"Failed to get system info: {e}"

def get_battery_status():
    """Get battery status"""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            status = "Charging" if battery.power_plugged else "Discharging"
            return f"🔋 Battery: {battery.percent}% ({status})"
        else:
            return "🔋 Battery information not available"
    except Exception as e:
        return f"Failed to get battery status: {e}"

def get_memory_usage():
    """Get memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        return f"💾 Memory Usage: {memory.percent}% ({memory.used // (1024**3)} GB / {memory.total // (1024**3)} GB)"
    except Exception as e:
        return f"Failed to get memory usage: {e}"

def get_cpu_usage():
    """Get CPU usage"""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        return f"🖥️ CPU Usage: {cpu_percent}%"
    except Exception as e:
        return f"Failed to get CPU usage: {e}"

def get_disk_space():
    """Get disk space information"""
    try:
        import psutil
        disk = psutil.disk_usage('/')
        total_gb = disk.total // (1024**3)
        used_gb = disk.used // (1024**3)
        free_gb = disk.free // (1024**3)
        return f"💿 Disk Space: {used_gb} GB used / {total_gb} GB total ({free_gb} GB free)"
    except Exception as e:
        return f"Failed to get disk space: {e}" 

# Smart Query Classifier and Executor
def smart_query_classifier(query: str) -> dict:
    """
    Smart query classifier that extracts information from natural language queries
    Returns a structured dictionary with action, target, parameters, and confidence
    """
    query_lower = query.lower()
    result = {
        "action": None,
        "target": None,
        "parameters": {},
        "confidence": 0.0,
        "raw_query": query
    }
    
    # 📊 Excel Automation
    if any(word in query_lower for word in ["excel", "spreadsheet", "workbook", "worksheet", "cell", "formula", "chart", "graph", "sort", "filter", "format", "data", "analysis"]):
        result["action"] = "excel_automation"
        result["target"] = "excel"
        result["parameters"]["query"] = query
        result["confidence"] = 0.9
    
    # 🎵 Music and Entertainment
    elif any(word in query_lower for word in ["play", "music", "song", "track", "album", "listen"]):
        result["action"] = "play_music"
        result["confidence"] = 0.9
        
        # Extract music information
        music_query = query_lower
        action_words = ["play", "music", "song", "track", "album", "listen", "put", "on"]
        for word in action_words:
            music_query = music_query.replace(word, "").strip()
        
        # Detect service
        if "spotify" in query_lower:
            result["target"] = "spotify"
            result["parameters"]["query"] = music_query.replace("spotify", "").strip()
        elif "youtube" in query_lower or "yt" in query_lower:
            result["target"] = "youtube"
            result["parameters"]["query"] = music_query.replace("youtube", "").replace("yt", "").strip()
        else:
            # Default to Spotify for music
            result["target"] = "spotify"
            result["parameters"]["query"] = music_query
    
    # 🖥️ System Commands
    elif any(word in query_lower for word in ["sleep", "restart", "shutdown", "lock", "screenshot", "camera"]):
        if "sleep" in query_lower or "laptop to sleep" in query_lower:
            result["action"] = "system_control"
            result["target"] = "sleep"
            result["confidence"] = 0.95
        elif "restart" in query_lower:
            result["action"] = "system_control"
            result["target"] = "restart"
            result["confidence"] = 0.95
        elif "shutdown" in query_lower or "shut down" in query_lower:
            result["action"] = "system_control"
            result["target"] = "shutdown"
            result["confidence"] = 0.95
        elif "lock" in query_lower:
            result["action"] = "system_control"
            result["target"] = "lock"
            result["confidence"] = 0.95
        elif "screenshot" in query_lower:
            result["action"] = "system_control"
            result["target"] = "screenshot"
            result["confidence"] = 0.95
        elif "camera" in query_lower:
            result["action"] = "system_control"
            result["target"] = "camera"
            result["confidence"] = 0.95
    
    # 📊 System Information
    elif any(word in query_lower for word in ["system info", "battery", "memory", "cpu", "disk space", "system status"]):
        if "system info" in query_lower or "system status" in query_lower:
            result["action"] = "system_info"
            result["target"] = "system_info"
            result["confidence"] = 0.9
        elif "battery" in query_lower:
            result["action"] = "system_info"
            result["target"] = "battery"
            result["confidence"] = 0.9
        elif "memory" in query_lower:
            result["action"] = "system_info"
            result["target"] = "memory"
            result["confidence"] = 0.9
        elif "cpu" in query_lower:
            result["action"] = "system_info"
            result["target"] = "cpu"
            result["confidence"] = 0.9
        elif "disk space" in query_lower or "disk" in query_lower:
            result["action"] = "system_info"
            result["target"] = "disk"
            result["confidence"] = 0.9
    
    # 🎮 Applications (check this before file operations)
    elif any(word in query_lower for word in ["open", "launch", "start", "run"]):
        result["action"] = "open_app"
        result["confidence"] = 0.8
        
        # Extract app name
        app_keywords = ["open", "launch", "start", "run", "app", "application"]
        app_query = query_lower
        
        for keyword in app_keywords:
            app_query = app_query.replace(keyword, "").strip()
        
        # Map common app names
        app_mapping = {
            "spotify": "spotify",
            "chrome": "chrome",
            "discord": "discord",
            "steam": "steam",
            "word": "word",
            "excel": "excel",
            "powerpoint": "powerpoint",
            "outlook": "outlook",
            "notepad": "notepad",
            "calculator": "calculator",
            "camera": "camera",
            "terminal": "terminal",
            "visual studio": "vscode",
            "vs code": "vscode",
            "photoshop": "photoshop",
            "vlc": "vlc",
            "whatsapp": "whatsapp",
            "telegram": "telegram",
            "teams": "teams",
            "zoom": "zoom",
            "skype": "skype",
            "netflix": "netflix",
            "youtube app": "youtube_app",
            "task manager": "task_manager",
            "settings": "settings",
            "control panel": "control_panel",
            "device manager": "device_manager",
            "desktop": "desktop",
            "documents": "documents",
            "downloads": "downloads",
            "pictures": "pictures",
            "videos": "videos",
            "music folder": "music_folder"
        }
        
        for app_name, app_id in app_mapping.items():
            if app_name in app_query:
                result["target"] = app_id
                result["confidence"] = 0.9
                break
        
        if not result["target"]:
            result["target"] = app_query
            result["confidence"] = 0.6
    
    # 📁 File and Drive Operations
    elif any(word in query_lower for word in ["drive", "folder", "file", "desktop", "documents", "downloads"]):
        if "d drive" in query_lower or "d:" in query_lower:
            result["action"] = "open_drive"
            result["target"] = "D"
            result["confidence"] = 0.9
        elif "c drive" in query_lower or "c:" in query_lower:
            result["action"] = "open_drive"
            result["target"] = "C"
            result["confidence"] = 0.9
        elif "desktop" in query_lower:
            result["action"] = "open_folder"
            result["target"] = "desktop"
            result["confidence"] = 0.9
        elif "documents" in query_lower:
            result["action"] = "open_folder"
            result["target"] = "documents"
            result["confidence"] = 0.9
        elif "downloads" in query_lower:
            result["action"] = "open_folder"
            result["target"] = "downloads"
            result["confidence"] = 0.9
        elif "pictures" in query_lower:
            result["action"] = "open_folder"
            result["target"] = "pictures"
            result["confidence"] = 0.9
        elif "videos" in query_lower:
            result["action"] = "open_folder"
            result["target"] = "videos"
            result["confidence"] = 0.9
        elif "music folder" in query_lower:
            result["action"] = "open_folder"
            result["target"] = "music_folder"
            result["confidence"] = 0.9
    
    # 🔍 Search Operations
    elif "search" in query_lower:
        result["action"] = "search"
        result["confidence"] = 0.8
        
        search_query = query_lower.replace("search", "").replace("for", "").strip()
        if search_query:
            result["parameters"]["query"] = search_query
            result["confidence"] = 0.9
        else:
            result["confidence"] = 0.5
    
    # 🎯 Advanced Automation
    elif any(word in query_lower for word in ["clean", "organize", "backup"]):
        if "clean desktop" in query_lower:
            result["action"] = "automation"
            result["target"] = "clean_desktop"
            result["confidence"] = 0.9
        elif "organize files" in query_lower:
            result["action"] = "automation"
            result["target"] = "organize_files"
            result["confidence"] = 0.9
        elif "backup files" in query_lower:
            result["action"] = "automation"
            result["target"] = "backup_files"
            result["confidence"] = 0.9
    
    # 🖥️ Screen Vision
    elif any(word in query_lower for word in ["analyze screen", "see screen", "screen monitoring"]):
        if "analyze screen" in query_lower or "see screen" in query_lower:
            result["action"] = "screen_vision"
            result["target"] = "analyze"
            result["confidence"] = 0.9
        elif "screen monitoring" in query_lower:
            result["action"] = "screen_vision"
            result["target"] = "monitor"
            result["confidence"] = 0.9
    
    # Volume Control
    elif any(word in query_lower for word in ["volume", "mute", "unmute"]):
        if "mute" in query_lower:
            result["action"] = "volume_control"
            result["target"] = "mute"
            result["confidence"] = 0.9
        elif "unmute" in query_lower:
            result["action"] = "volume_control"
            result["target"] = "unmute"
            result["confidence"] = 0.9
        elif "volume up" in query_lower or "increase volume" in query_lower:
            result["action"] = "volume_control"
            result["target"] = "volume_up"
            result["confidence"] = 0.9
        elif "volume down" in query_lower or "decrease volume" in query_lower:
            result["action"] = "volume_control"
            result["target"] = "volume_down"
            result["confidence"] = 0.9
    
    return result

def execute_smart_command(classification: dict) -> str:
    """
    Execute commands based on smart classification
    """
    try:
        action = classification["action"]
        target = classification["target"]
        parameters = classification.get("parameters", {})
        
        print(f"🎯 Executing: {action} -> {target} with params: {parameters}")
        
        if action == "play_music":
            if target == "spotify":
                query = parameters.get("query", "")
                return PlayMusic(f"spotify {query}")
            elif target == "youtube":
                query = parameters.get("query", "")
                return PlayMusic(f"youtube {query}")
        
        elif action == "system_control":
            if target == "sleep":
                return System("sleep")
            elif target == "restart":
                return System("restart")
            elif target == "shutdown":
                return System("shutdown")
            elif target == "lock":
                return System("lock")
            elif target == "screenshot":
                return System("screenshot")
            elif target == "camera":
                return System("camera")
        
        elif action == "system_info":
            if target == "system_info":
                return get_system_info()
            elif target == "battery":
                return get_battery_status()
            elif target == "memory":
                return get_memory_usage()
            elif target == "cpu":
                return get_cpu_usage()
            elif target == "disk":
                return get_disk_space()
        
        elif action == "open_app":
            # Map app IDs to actual function calls
            app_mapping = {
                "spotify": lambda: open_spotify_specific(),
                "chrome": lambda: open_chrome(),
                "discord": lambda: open_discord(),
                "steam": lambda: open_steam(),
                "word": lambda: open_word(),
                "excel": lambda: open_excel(),
                "powerpoint": lambda: open_powerpoint(),
                "outlook": lambda: open_outlook(),
                "notepad": lambda: open_notepad(),
                "calculator": lambda: open_calculator(),
                "camera": lambda: open_camera(),
                "terminal": lambda: open_terminal(),
                "vscode": lambda: open_vscode(),
                "photoshop": lambda: open_photoshop(),
                "vlc": lambda: open_vlc(),
                "whatsapp": lambda: open_whatsapp(),
                "telegram": lambda: open_telegram(),
                "teams": lambda: open_teams(),
                "zoom": lambda: open_zoom(),
                "skype": lambda: open_skype(),
                "netflix": lambda: open_netflix(),
                "youtube_app": lambda: open_youtube_app(),
                "task_manager": lambda: open_task_manager(),
                "settings": lambda: open_settings(),
                "control_panel": lambda: open_control_panel(),
                "device_manager": lambda: open_device_manager(),
                "desktop": lambda: open_desktop(),
                "documents": lambda: open_documents(),
                "downloads": lambda: open_downloads(),
                "pictures": lambda: open_pictures(),
                "videos": lambda: open_videos(),
                "music_folder": lambda: open_music_folder()
            }
            
            if target in app_mapping:
                return app_mapping[target]()
            else:
                return OpenApp(target)
        
        elif action == "open_drive":
            return System(f"{target} drive")
        
        elif action == "open_folder":
            folder_mapping = {
                "desktop": lambda: open_desktop(),
                "documents": lambda: open_documents(),
                "downloads": lambda: open_downloads(),
                "pictures": lambda: open_pictures(),
                "videos": lambda: open_videos(),
                "music_folder": lambda: open_music_folder()
            }
            
            if target in folder_mapping:
                return folder_mapping[target]()
        
        elif action == "search":
            query = parameters.get("query", "")
            if query:
                # Use GoogleSearch for web searches
                return GoogleSearch(query)
            else:
                return "Please specify what to search for"
        
        elif action == "automation":
            if target == "clean_desktop":
                return clean_desktop()
            elif target == "organize_files":
                return organize_files()
            elif target == "backup_files":
                return backup_files()
        
        elif action == "screen_vision":
            if target == "analyze":
                if SCREEN_VISION_AVAILABLE:
                    analysis = capture_and_analyze("analyze current screen")
                    return f"Screen analyzed: {analysis[:100]}..."
                else:
                    return "Screen vision not available"
            elif target == "monitor":
                if SCREEN_VISION_AVAILABLE:
                    start_screen_monitoring()
                    return "Screen monitoring started"
                else:
                    return "Screen vision not available"
        
        elif action == "volume_control":
            if target == "mute":
                return System("mute")
            elif target == "unmute":
                return System("unmute")
            elif target == "volume_up":
                return System("volume up")
            elif target == "volume_down":
                return System("volume down")
        
        elif action == "excel_automation":
            if EXCEL_AUTOMATION_AVAILABLE:
                query = parameters.get("query", "")
                return handle_excel_request(query)
            else:
                return "Excel automation is not available. Please install required dependencies."
        
        else:
            return f"Unknown action: {action}"
            
    except Exception as e:
        print(f"❌ Error executing smart command: {e}")
        return f"Error executing command: {str(e)}"

def smart_automation(query: str) -> str:
    """
    Main smart automation function that uses query classification
    """
    try:
        print(f"🎯 Smart automation analyzing: {query}")
        
        # Classify the query
        classification = smart_query_classifier(query)
        
        print(f"📊 Classification: {classification}")
        
        # Check confidence threshold
        if classification["confidence"] < 0.5:
            return f"Could not understand: {query}. Please try a more specific command."
        
        # Execute the command
        result = execute_smart_command(classification)
        
        return result
        
    except Exception as e:
        print(f"❌ Smart automation error: {e}")
        return f"Error in smart automation: {str(e)}"

# Advanced Spotify Controls
def spotify_advanced_control(command: str, query: str = "") -> str:
    """
    Advanced Spotify control with pause, skip, volume, etc.
    """
    try:
        import pyautogui
        import time
        
        print(f"🎵 Spotify Advanced Control: {command}")
        
        # First, ensure Spotify is active
        try:
            spotify_windows = pyautogui.getWindowsWithTitle("Spotify")
            if spotify_windows:
                spotify_windows[0].activate()
                time.sleep(0.5)
            else:
                # Try to open Spotify if not running
                open_spotify_specific()
                time.sleep(2)
        except:
            pass
        
        if command == "play":
            if query:
                return PlayMusic(f"spotify {query}")
            else:
                # Just play/pause current
                pyautogui.press('space')
                return "Toggled Spotify play/pause"
        
        elif command == "pause":
            pyautogui.press('space')
            return "Paused Spotify"
        
        elif command == "skip":
            pyautogui.press('nexttrack')  # or 'ctrl+right'
            return "Skipped to next track"
        
        elif command == "previous":
            pyautogui.press('prevtrack')  # or 'ctrl+left'
            return "Previous track"
        
        elif command == "volume_up":
            pyautogui.press('volumeup')
            return "Volume increased"
        
        elif command == "volume_down":
            pyautogui.press('volumedown')
            return "Volume decreased"
        
        elif command == "mute":
            pyautogui.press('volumemute')
            return "Volume muted"
        
        elif command == "shuffle":
            pyautogui.press('ctrl+s')
            return "Toggled shuffle"
        
        elif command == "repeat":
            pyautogui.press('ctrl+r')
            return "Toggled repeat"
        
        else:
            return f"Unknown Spotify command: {command}"
            
    except Exception as e:
        print(f"❌ Spotify control error: {e}")
        return f"Failed to control Spotify: {str(e)}"

# Enhanced Query Classifier with Spotify Controls and Command Line Automation
def enhanced_query_classifier(query: str) -> dict:
    """
    Enhanced query classifier that includes Spotify controls, Excel automation, and Command Line automation
    """
    query_lower = query.lower()
    result = {
        "action": None,
        "target": None,
        "parameters": {},
        "confidence": 0.0,
        "raw_query": query
    }
    
    # Command Line Automation (check this first for installation/command requests)
    command_line_keywords = [
        "install", "get", "download", "add", "setup", "run command", "execute", "cmd", "terminal", "shell", "run", "do",
        "system info", "disk space", "memory info", "cpu info", "network info", "processes", "services", "shutdown", 
        "restart", "sleep", "hibernate", "clean temp", "disk cleanup", "defrag", "check disk", "sfc scan", 
        "windows update", "firewall status", "network reset", "dns flush", "ping", "tracert", "nslookup", 
        "whoami", "hostname", "date", "time", "dir", "list files", "tree", "copy", "move", "delete", "mkdir", 
        "rmdir", "cd", "echo", "type", "find", "sort", "cls", "clear", "help", "ver", "show", "display", "check", 
        "scan", "clean", "reset", "flush"
    ]
    
    # Check for specific package installations
    package_names = [
        "git", "python", "node", "vscode", "chrome", "firefox", "spotify", "discord", "steam", "obs", "vlc", "blender", 
        "gimp", "audacity", "7zip", "winrar", "notepad++", "sublime", "atom", "postman", "docker", "wsl", "ubuntu", 
        "debian", "kali", "java", "rust", "go", "ruby", "php", "mysql", "postgresql", "mongodb", "aws", "azure", 
        "teams", "slack", "zoom", "skype", "telegram", "office", "adobe", "epic", "origin", "uplay", "battle.net",
        "cpu-z", "gpu-z", "hwinfo", "ccleaner", "defraggler", "recuva", "bitdefender", "kaspersky", "mcafee"
    ]
    
    if any(keyword in query_lower for keyword in command_line_keywords) or any(package in query_lower for package in package_names):
        result["action"] = "command_line_automation"
        result["target"] = "command_line"
        result["parameters"]["query"] = query
        result["confidence"] = 0.9
    
    # Excel Automation
    elif any(word in query_lower for word in ["excel", "spreadsheet", "workbook", "worksheet", "cell", "formula", "chart", "graph", "sort", "filter", "format", "data", "analysis"]):
        result["action"] = "excel_automation"
        result["target"] = "excel"
        result["parameters"]["query"] = query
        result["confidence"] = 0.9
    
    # Gmail Automation
    elif any(word in query_lower for word in ["draft email", "compose email", "write email", "create email", "prepare email"]):
        result["action"] = "gmail_automation"
        result["target"] = "draft_email"
        result["parameters"]["query"] = query
        result["confidence"] = 0.95
    elif any(word in query_lower for word in ["send email", "mail", "email", "gmail"]) and any(word in query_lower for word in ["send", "mail", "email"]):
        result["action"] = "gmail_automation"
        result["target"] = "send_email"
        result["parameters"]["query"] = query
        result["confidence"] = 0.9
    elif any(word in query_lower for word in ["open gmail", "gmail", "mail"]):
        result["action"] = "gmail_automation"
        result["target"] = "open_gmail"
        result["parameters"]["query"] = query
        result["confidence"] = 0.9
    
    # Spotify Controls
    elif "spotify" in query_lower:
        if any(word in query_lower for word in ["pause", "stop"]):
            result["action"] = "spotify_control"
            result["target"] = "pause"
            result["confidence"] = 0.95
        elif any(word in query_lower for word in ["skip", "next"]):
            result["action"] = "spotify_control"
            result["target"] = "skip"
            result["confidence"] = 0.95
        elif any(word in query_lower for word in ["previous", "back"]):
            result["action"] = "spotify_control"
            result["target"] = "previous"
            result["confidence"] = 0.95
        elif any(word in query_lower for word in ["shuffle"]):
            result["action"] = "spotify_control"
            result["target"] = "shuffle"
            result["confidence"] = 0.95
        elif any(word in query_lower for word in ["repeat", "loop"]):
            result["action"] = "spotify_control"
            result["target"] = "repeat"
            result["confidence"] = 0.95
        elif any(word in query_lower for word in ["play", "music", "song"]):
            # Extract song name - remove "on" from the end
            music_query = query_lower.replace("spotify", "").replace("play", "").replace("music", "").replace("song", "").strip()
            # Remove "on" from the end if it's there
            if music_query.endswith(" on"):
                music_query = music_query[:-3].strip()
            result["action"] = "play_music"
            result["target"] = "spotify"
            result["parameters"]["query"] = music_query
            result["confidence"] = 0.9
    
    # Use the original smart classifier for other commands
    else:
        original_result = smart_query_classifier(query)
        result.update(original_result)
    
    return result

def execute_enhanced_command(classification: dict) -> str:
    """
    Execute commands with enhanced Spotify controls and Command Line automation
    """
    try:
        action = classification["action"]
        target = classification["target"]
        parameters = classification.get("parameters", {})
        
        print(f"🎯 Enhanced Execution: {action} -> {target}")
        
        if action == "command_line_automation":
            if COMMAND_LINE_AUTOMATION_AVAILABLE:
                query = parameters.get("query", "")
                return handle_command_line_request(query)
            else:
                return "Command line automation is not available. Please check the installation."
        elif action == "spotify_control":
            return spotify_advanced_control(target)
        elif action == "gmail_automation":
            if GMAIL_AUTOMATION_AVAILABLE:
                query = parameters.get("query", "")
                return handle_gmail_request(query)
            else:
                return "Gmail automation is not available. Please install required dependencies."
        elif action == "excel_automation":
            if EXCEL_AUTOMATION_AVAILABLE:
                query = parameters.get("query", "")
                return handle_excel_request(query)
            else:
                return "Excel automation is not available. Please install required dependencies."
        else:
            # Use the original smart command execution
            return execute_smart_command(classification)
            
    except Exception as e:
        print(f"❌ Error executing enhanced command: {e}")
        return f"Error executing command: {str(e)}"

def enhanced_automation(query: str) -> str:
    """
    Enhanced automation with Spotify controls
    """
    try:
        print(f"🎯 Enhanced automation analyzing: {query}")
        
        # Use enhanced classification
        classification = enhanced_query_classifier(query)
        
        print(f"📊 Enhanced Classification: {classification}")
        
        # Check confidence threshold
        if classification["confidence"] < 0.5:
            return f"Could not understand: {query}. Please try a more specific command."
        
        # Execute the command
        result = execute_enhanced_command(classification)
        
        return result
        
    except Exception as e:
        print(f"❌ Enhanced automation error: {e}")
        return f"Error in enhanced automation: {str(e)}" 

def GoogleSearch(Topic):
    try:
        if PYWHATKIT_AVAILABLE:
            # Use web browser search as fallback since pywhatkit search has issues
            search_url = f"https://www.google.com/search?q={Topic.replace(' ', '+')}"
            webbrowser.open(search_url)
        else:
            # Fallback to web browser search
            search_url = f"https://www.google.com/search?q={Topic.replace(' ', '+')}"
            webbrowser.open(search_url)
        return True
    except Exception as e:
        print(f"⚠️ Search failed: {e}")
        # Fallback to web browser search
        try:
            search_url = f"https://www.google.com/search?q={Topic.replace(' ', '+')}"
            webbrowser.open(search_url)
            return True
        except Exception as e2:
            print(f"⚠️ Fallback search also failed: {e2}")
            return False

def Content(Topic):
    """Generate content for various types of documents (excluding emails)"""
    
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])
        
    def ContentWriterAI(prompt):
        messages = [{"role": "user", "content": f"{prompt}"}]
        
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
        return Answer
    
    Topic: str = Topic.replace("Content", "").strip()
    
    # Check if this is an email request - if so, let Gmail integration handle it
    if any(keyword in Topic.lower() for keyword in ["email", "mail", "e-mail", "send email", "draft email"]):
        return "For email functionality, please use Gmail commands like 'draft an email to [address] about [subject] saying [message]' or 'send email to [address] subject [subject] body [message]'"
    
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

def PlayMusic(query):
    """Enhanced music playbook function that can handle different music services"""
    try:
        query_lower = query.lower()
        print(f"PlayMusic received: {query}")
        
        # Check if it's a Spotify request
        if "spotify" in query_lower:
            # Extract the song/artist from the query
            music_query = query_lower.replace("spotify", "").replace("play", "").strip()
            print(f"Extracted music query: '{music_query}'")
            
            if music_query:
                # First try to open Spotify using specialized method
                print("Opening Spotify using specialized method...")
                if open_spotify_specific():
                    print("Spotify opened successfully, waiting for app to load...")
                    import time
                    time.sleep(3)  # Wait for Spotify to load
                    
                    # Use Spotify protocol to search and then automate playback
                    try:
                        # Use Spotify protocol for direct search
                        spotify_search_protocol = f"spotify:search:{music_query.replace(' ', '%20')}"
                        print(f"Trying Spotify protocol: {spotify_search_protocol}")
                        subprocess.run(["start", spotify_search_protocol], shell=True)
                        
                        # Wait for the search to load, then use GUI automation to play
                        time.sleep(3)
                        print("Protocol search initiated, now attempting GUI automation to play...")
                        
                        # Use the enhanced desktop automation to play the first result (skip search since protocol already did it)
                        if spotify_desktop_search(music_query, skip_search=True):
                            return f"✅ Successfully searched and played first result for '{music_query}' in Spotify"
                        else:
                            # Even if automation fails, the search was successful, so inform user
                            return f"✅ Searched for '{music_query}' in Spotify. First result should be ready to play."
                            
                    except Exception as e:
                        print(f"Spotify protocol failed: {e}")
                        
                        # Fallback: Use advanced desktop automation directly
                        if spotify_desktop_search(music_query):
                            return f"✅ Successfully searched and played first result for '{music_query}' in Spotify"
                        else:
                            # Even if automation fails, the search was successful, so inform user
                            return f"✅ Searched for '{music_query}' in Spotify. First result should be ready to play."
                else:
                    print("Desktop Spotify failed, trying web version")
                    # Fallback to web version only if desktop completely fails
                    search_url = f"https://open.spotify.com/search/{music_query.replace(' ', '%20')}"
                    webbrowser.open(search_url)
                    return f"✅ Opened Spotify web and searching for: {music_query}. First result should be ready to play."
            else:
                # Just open Spotify without search
                print("No music query provided, just opening Spotify")
                if open_spotify_specific():
                    return "Opened Spotify desktop application"
                else:
                    webbrowser.open("https://open.spotify.com")
                    return "Opened Spotify web application"
        
        # Check if it's a YouTube Music request
        elif "youtube music" in query_lower or "yt music" in query_lower:
            music_query = query_lower.replace("youtube music", "").replace("yt music", "").replace("play", "").strip()
            if music_query:
                search_url = f"https://music.youtube.com/search?q={music_query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"Opened YouTube Music and searching for: {music_query}"
        
        # Check if it's a general YouTube request
        elif "youtube" in query_lower:
            music_query = query_lower.replace("youtube", "").replace("play", "").strip()
            if music_query:
                # Use pywhatkit for YouTube playback
                try:
                    playonyt(music_query)
                    return f"Playing on YouTube: {music_query}"
                except:
                    # Fallback to search
                    search_url = f"https://www.youtube.com/results?search_query={music_query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    return f"Opened YouTube search for: {music_query}"
        
        # Default to YouTube if no specific service mentioned
        else:
            try:
                playonyt(query)
                return f"Playing on YouTube: {query}"
            except:
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"Opened YouTube search for: {query}"
                
    except Exception as e:
        print(f"Error in PlayMusic: {e}")
        # Fallback to YouTube search
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Opened YouTube search for: {query}"

def PlayYoutube(query):
    playonyt(query)
    return True

# Gmail automation functions removed - will be replaced from pragna-email branch