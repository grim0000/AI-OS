# 🤖 AI Voice Assistant with Screen Vision

A powerful AI voice assistant with real-time screen vision capabilities, built with Python and PyQt5.

## ✨ Features

### 🎵 **Smart Music Control**
- **Spotify Desktop Integration**: Opens desktop app and automatically plays first search result
- **Intelligent Click Detection**: Uses computer vision to find and click on search results
- **Multiple Fallback Methods**: Keyboard navigation, window-based clicking, and AI vision

### 🖥️ **Screen Vision System**
- **Real-time Screen Capture**: Captures and analyzes your screen in real-time
- **Computer Vision Analysis**: Detects UI elements, buttons, and clickable areas
- **Spotify Interface Recognition**: Specialized detection for Spotify's green branding and interface

### 🗣️ **Voice Commands**
- **"Open Spotify and play [song name]"** - Searches and plays music
- **"Analyze screen"** - Analyzes current screen content
- **"Open D drive"** - Opens file explorer
- **"Put my laptop to sleep"** - System control
- **"Open camera"** - Opens Windows Camera
- **"Take a screenshot"** - Takes screenshots
- **"Lock my computer"** - Locks the system

### 📧 **Email & Content Creation**
- **Interactive Email Drafting**: Asks follow-up questions for better emails
- **Gmail Integration**: Automated email sending
- **Content Writing**: Letters, reports, articles, applications

### 🎨 **Modern GUI**
- **Heartbeat Animation**: Visual feedback during AI responses
- **Audio Device Selection**: Dropdown for input/output devices
- **Side Chat Panel**: Chat history on the left side
- **Real-time Status**: Shows listening, thinking, and response states

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd jarvis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r Requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with:
   ```
   GroqAPIKey=your_groq_api_key
   Username=YourName
   AssistantName=Jarvis
   ```

5. **Run the application**
   ```bash
   python Main.py
   ```

## 🎯 Usage

### Voice Commands

#### Music Control
- **"Open Spotify and play [song name]"** - Searches and plays the first result
- **"Play [song] on Spotify"** - Alternative command

#### System Control
- **"Put my laptop to sleep"** - Sleep mode
- **"Open camera"** - Windows Camera app
- **"Open D drive"** - File explorer
- **"Take a screenshot"** - Screenshot to clipboard
- **"Lock my computer"** - Lock system
- **"Restart computer"** - Restart system
- **"Shutdown computer"** - Shutdown system

#### 🎮 Gaming & Entertainment
- **"Open Steam"** - Steam gaming platform
- **"Open Epic Games"** - Epic Games Launcher
- **"Open Discord"** - Discord app
- **"Open Netflix"** - Netflix app
- **"Open YouTube app"** - YouTube desktop app

#### 📱 Communication & Social
- **"Open WhatsApp"** - WhatsApp desktop
- **"Open Telegram"** - Telegram desktop
- **"Open Teams"** - Microsoft Teams
- **"Open Zoom"** - Zoom desktop app
- **"Open Skype"** - Skype desktop

#### 💼 Productivity & Office
- **"Open Word"** - Microsoft Word
- **"Open Excel"** - Microsoft Excel
- **"Open PowerPoint"** - Microsoft PowerPoint
- **"Open Outlook"** - Microsoft Outlook
- **"Open Chrome"** - Google Chrome
- **"Open Firefox"** - Mozilla Firefox
- **"Open Edge"** - Microsoft Edge

#### 🎨 Creative & Design
- **"Open Photoshop"** - Adobe Photoshop
- **"Open Illustrator"** - Adobe Illustrator
- **"Open Premiere"** - Adobe Premiere Pro
- **"Open Blender"** - Blender 3D
- **"Open OBS"** - OBS Studio

#### 🔧 Development & Programming
- **"Open VS Code"** - Visual Studio Code
- **"Open PyCharm"** - PyCharm IDE
- **"Open IntelliJ"** - IntelliJ IDEA
- **"Open Git Bash"** - Git Bash terminal
- **"Open Terminal"** - Command Prompt
- **"Open PowerShell"** - PowerShell

#### 📊 System & Utilities
- **"Open Task Manager"** - Windows Task Manager
- **"Open Control Panel"** - Windows Control Panel
- **"Open Settings"** - Windows Settings
- **"Open Device Manager"** - Device Manager
- **"Run Disk Cleanup"** - Disk Cleanup utility
- **"Run Defrag"** - Disk Defragmenter

#### 🎵 Media & Audio
- **"Open VLC"** - VLC Media Player
- **"Open Windows Media Player"** - Windows Media Player
- **"Open Groove Music"** - Groove Music
- **"Open Audacity"** - Audacity audio editor

#### 📁 File Operations
- **"Open Desktop"** - Desktop folder
- **"Open Documents"** - Documents folder
- **"Open Downloads"** - Downloads folder
- **"Open Pictures"** - Pictures folder
- **"Open Videos"** - Videos folder
- **"Open Music folder"** - Music folder

#### 🔒 Security & Privacy
- **"Open Windows Defender"** - Windows Defender
- **"Open Firewall"** - Windows Firewall
- **"Open BitLocker"** - BitLocker Drive Encryption

#### 🌐 Network & Internet
- **"Open Network Settings"** - Network Settings
- **"Open WiFi Settings"** - WiFi Settings
- **"Open Ethernet Settings"** - Ethernet Settings

#### 🎯 Advanced Automation
- **"Clean Desktop"** - Organize desktop files
- **"Organize Files"** - Organize current directory
- **"Backup Files"** - Create backup of important folders
- **"System Info"** - Get system information
- **"Battery Status"** - Check battery status
- **"Memory Usage"** - Check memory usage
- **"CPU Usage"** - Check CPU usage
- **"Disk Space"** - Check disk space

#### Screen Analysis
- **"Analyze screen"** - Analyze current screen
- **"See screen"** - Screen analysis
- **"Start screen monitoring"** - Continuous monitoring

#### File Operations
- **"Search for [file/folder]"** - Windows search
- **"Open [app name]"** - Launch applications

## 🛠️ Technical Details

### Core Components

- **`Main.py`** - Main application entry point
- **`Backend/Automation.py`** - System automation and app control
- **`Backend/ScreenVision.py`** - Real-time screen capture and analysis
- **`Backend/Model.py`** - AI model for query classification
- **`Backend/SpeechToText.py`** - Voice recognition
- **`Backend/TextToSpeech.py`** - Text-to-speech synthesis
- **`Frontend/ModernGUI.py`** - PyQt5-based user interface

### Screen Vision System

The screen vision system uses:
- **OpenCV** for computer vision analysis
- **MSS** for screen capture
- **Computer vision algorithms** for UI element detection
- **Spotify-specific detection** for music automation

### Spotify Automation

The Spotify automation uses multiple methods:
1. **Keyboard Navigation** (most reliable)
2. **Window-based Clicking** (multiple positions)
3. **AI Vision Detection** (precise targeting)
4. **Fallback Shortcuts** (various Spotify controls)

## 🔧 Configuration

### Audio Devices
- Select input/output devices from dropdown menus
- Supports all Windows audio devices
- Real-time device switching

### Environment Variables
- `GroqAPIKey`: Your Groq API key for AI processing
- `Username`: Your name for personalization
- `AssistantName`: Assistant's name (default: Jarvis)

## 📁 Project Structure

```
jarvis/
├── Main.py                 # Main application
├── Requirements.txt        # Dependencies
├── Backend/               # Core functionality
│   ├── Automation.py      # System automation
│   ├── ScreenVision.py    # Screen vision system
│   ├── Model.py          # AI model
│   ├── SpeechToText.py   # Voice recognition
│   ├── TextToSpeech.py   # Text-to-speech
│   ├── Chatbot.py        # Chat functionality
│   ├── InteractiveDrafting.py  # Email drafting
│   └── GmailIntegration.py     # Gmail automation
├── Frontend/             # User interface
│   ├── ModernGUI.py      # Main GUI
│   ├── Files/           # Temporary files
│   └── Graphics/        # UI graphics
└── Data/                # Data storage
    ├── ChatLog.json     # Chat history
    └── Voice.html       # Voice interface
```

## 🎉 Features Summary

✅ **Real-time screen vision**  
✅ **Smart Spotify automation**  
✅ **Voice-controlled system**  
✅ **Modern PyQt5 GUI**  
✅ **Email drafting & Gmail integration**  
✅ **Multiple automation commands**  
✅ **Audio device management**  
✅ **Heartbeat animations**  
✅ **Clean, organized codebase**  

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Enjoy your AI assistant! 🎵🤖✨**
#   O S A I M A - A I  
 