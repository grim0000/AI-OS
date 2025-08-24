import subprocess
import re
import os
import platform
import shutil
from typing import Dict, List, Tuple, Optional
import json

class CommandLineAutomation:
    """
    Handles command line operations like package installation, system commands, etc.
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_linux = self.system == "linux"
        self.is_macos = self.system == "darwin"
        
        # Package managers and their commands
        self.package_managers = {
            "windows": {
                "winget": "winget install",
                "choco": "choco install",
                "scoop": "scoop install",
                "npm": "npm install -g",
                "pip": "pip install",
                "pip3": "pip3 install"
            },
            "linux": {
                "apt": "sudo apt install",
                "apt-get": "sudo apt-get install",
                "yum": "sudo yum install",
                "dnf": "sudo dnf install",
                "pacman": "sudo pacman -S",
                "snap": "sudo snap install",
                "flatpak": "flatpak install",
                "npm": "sudo npm install -g",
                "pip": "pip install",
                "pip3": "pip3 install"
            },
            "darwin": {
                "brew": "brew install",
                "port": "sudo port install",
                "npm": "npm install -g",
                "pip": "pip install",
                "pip3": "pip3 install"
            }
        }
        
        # Enhanced package mappings with more applications
        self.package_mappings = {
            # Development tools
            "git": "Git.Git",
            "python": "Python.Python.3.11",
            "node": "OpenJS.NodeJS",
            "vscode": "Microsoft.VisualStudioCode",
            "sublime": "SublimeHQ.SublimeText",
            "atom": "GitHub.Atom",
            "notepad++": "Notepad++.Notepad++",
            "postman": "Postman.Postman",
            "docker": "Docker.DockerDesktop",
            "wsl": "Microsoft.WSL",
            
            # Browsers
            "chrome": "Google.Chrome",
            "firefox": "Mozilla.Firefox",
            "edge": "Microsoft.Edge",
            "opera": "Opera.Opera",
            "brave": "BraveSoftware.BraveBrowser",
            
            # Media and entertainment
            "spotify": "Spotify.Spotify",
            "discord": "Discord.Discord",
            "steam": "Valve.Steam",
            "obs": "OBSProject.OBSStudio",
            "vlc": "VideoLAN.VLC",
            "blender": "BlenderFoundation.Blender",
            "gimp": "GIMP.GIMP",
            "audacity": "Audacity.Audacity",
            "krita": "KDE.Krita",
            
            # Utilities
            "7zip": "7zip.7zip",
            "winrar": "RARLab.WinRAR",
            "ccleaner": "Piriform.CCleaner",
            "malwarebytes": "Malwarebytes.Malwarebytes",
            "avast": "Avast.AvastFreeAntivirus",
            "norton": "NortonLifeLock.NortonSecurity",
            
            # Linux distributions
            "ubuntu": "Canonical.Ubuntu",
            "debian": "Debian.Debian",
            "kali": "KaliLinux.KaliLinux",
            "fedora": "Fedora.Fedora",
            "centos": "CentOS.CentOS",
            
            # Programming languages and tools
            "java": "Oracle.JDK",
            "rust": "Rust.Rust",
            "go": "GoLang.Go",
            "ruby": "RubyInstallerTeam.Ruby",
            "php": "PHP.PHP",
            "composer": "Composer.Composer",
            
            # Database tools
            "mysql": "Oracle.MySQL",
            "postgresql": "PostgreSQL.PostgreSQL",
            "mongodb": "MongoDB.Server",
            "sqlite": "SQLite.SQLite",
            
            # Cloud and DevOps
            "aws": "Amazon.AWSCLI",
            "azure": "Microsoft.AzureCLI",
            "gcloud": "Google.CloudSDK",
            "terraform": "HashiCorp.Terraform",
            "kubernetes": "Kubernetes.kubectl",
            
            # Communication
            "teams": "Microsoft.Teams",
            "slack": "SlackTechnologies.Slack",
            "zoom": "Zoom.Zoom",
            "skype": "Microsoft.Skype",
            "telegram": "Telegram.TelegramDesktop",
            
            # Productivity
            "office": "Microsoft.Office",
            "libreoffice": "TheDocumentFoundation.LibreOffice",
            "adobe": "Adobe.AdobeCreativeCloud",
            "paint": "Microsoft.Paint",
            "calculator": "Microsoft.WindowsCalculator",
            
            # Gaming
            "epic": "EpicGames.EpicGamesLauncher",
            "origin": "ElectronicArts.EADesktop",
            "uplay": "Ubisoft.Connect",
            "battle.net": "Blizzard.BattleNet",
            
            # Security
            "bitdefender": "Bitdefender.Bitdefender",
            "kaspersky": "KasperskyLab.KasperskySecurity",
            "mcafee": "McAfee.McAfeeSecurity",
            
            # System tools
            "cpu-z": "CPUID.CPU-Z",
            "gpu-z": "TechPowerUp.GPU-Z",
            "hwinfo": "REALiX.HWiNFO",
            "ccleaner": "Piriform.CCleaner",
            "defraggler": "Piriform.Defraggler",
            "recuva": "Piriform.Recuva"
        }
        
        # Available package managers on this system
        self.available_managers = self._detect_available_managers()
        
        # Common system commands that can be executed
        self.system_commands = {
            "system info": "systeminfo",
            "system information": "systeminfo",
            "disk space": "wmic logicaldisk get size,freespace,caption",
            "memory info": "wmic computersystem get TotalPhysicalMemory",
            "cpu info": "wmic cpu get name",
            "network info": "ipconfig",
            "processes": "tasklist",
            "services": "net start",
            "shutdown": "shutdown /s /t 0",
            "restart": "shutdown /r /t 0",
            "sleep": "powercfg /hibernate off && rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
            "hibernate": "shutdown /h",
            "clean temp": "del /q /f %temp%\\*",
            "clean temp files": "del /q /f %temp%\\*",
            "disk cleanup": "cleanmgr",
            "defrag": "defrag C: /A",
            "check disk": "chkdsk C: /f",
            "sfc scan": "sfc /scannow",
            "dism restore": "DISM /Online /Cleanup-Image /RestoreHealth",
            "windows update": "wuauclt /detectnow",
            "firewall status": "netsh advfirewall show allprofiles",
            "network reset": "netsh winsock reset",
            "ip reset": "netsh int ip reset",
            "dns flush": "ipconfig /flushdns",
            "arp flush": "arp -d",
            "route print": "route print",
            "netstat": "netstat -an",
            "ping google": "ping google.com",
            "ping test": "ping 8.8.8.8",
            "tracert google": "tracert google.com",
            "nslookup google": "nslookup google.com",
            "whoami": "whoami",
            "hostname": "hostname",
            "date": "date",
            "time": "time",
            "dir": "dir",
            "list files": "dir",
            "show files": "dir",
            "tree": "tree",
            "show directory": "tree",
            "copy": "copy",
            "move": "move",
            "del": "del",
            "delete": "del",
            "mkdir": "mkdir",
            "make directory": "mkdir",
            "rmdir": "rmdir",
            "remove directory": "rmdir",
            "cd": "cd",
            "change directory": "cd",
            "pwd": "cd",
            "current directory": "cd",
            "echo": "echo",
            "type": "type",
            "find": "find",
            "findstr": "findstr",
            "sort": "sort",
            "more": "more",
            "less": "more",
            "cls": "cls",
            "clear": "cls",
            "clear screen": "cls",
            "help": "help",
            "version": "ver",
            "windows version": "ver",
            "os version": "ver"
        }
    
    def _detect_available_managers(self) -> List[str]:
        """Detect which package managers are available on the system"""
        available = []
        
        for manager in self.package_managers.get(self.system, {}).keys():
            if shutil.which(manager):
                available.append(manager)
        
        return available
    
    def _extract_package_name(self, query: str) -> Optional[str]:
        """Extract package name from user query"""
        query_lower = query.lower()
        
        # Enhanced installation patterns
        patterns = [
            r"install\s+([a-zA-Z0-9._-]+)",
            r"get\s+([a-zA-Z0-9._-]+)",
            r"download\s+([a-zA-Z0-9._-]+)",
            r"add\s+([a-zA-Z0-9._-]+)",
            r"setup\s+([a-zA-Z0-9._-]+)",
            r"([a-zA-Z0-9._-]+)\s+install",
            r"([a-zA-Z0-9._-]+)\s+setup",
            r"([a-zA-Z0-9._-]+)\s+download",
            r"([a-zA-Z0-9._-]+)\s+get"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1)
        
        # Direct package name mentions
        for package in self.package_mappings.keys():
            if package in query_lower:
                return package
        
        return None
    
    def _get_package_manager_command(self, package_name: str) -> Tuple[str, str]:
        """Get the best package manager and command for installing a package"""
        # Check if we have a specific mapping for this package
        mapped_package = self.package_mappings.get(package_name.lower(), package_name)
        
        # Prefer winget on Windows, apt on Linux, brew on macOS
        preferred_order = {
            "windows": ["winget", "choco", "scoop", "npm", "pip"],
            "linux": ["apt", "apt-get", "dnf", "yum", "snap", "flatpak", "npm", "pip"],
            "darwin": ["brew", "port", "npm", "pip"]
        }
        
        for manager in preferred_order.get(self.system, []):
            if manager in self.available_managers:
                base_command = self.package_managers[self.system][manager]
                return manager, f"{base_command} {mapped_package}"
        
        # Fallback to first available manager
        if self.available_managers:
            manager = self.available_managers[0]
            base_command = self.package_managers[self.system][manager]
            return manager, f"{base_command} {package_name}"
        
        return None, None
    
    def _extract_system_command(self, query: str) -> Optional[str]:
        """Extract system command from user query"""
        query_lower = query.lower()
        
        # Check for exact matches in system commands
        for command_name, command in self.system_commands.items():
            if command_name in query_lower:
                return command
        
        # Enhanced command patterns
        command_patterns = [
            r"run\s+(?:command\s+)?(.+)",
            r"execute\s+(.+)",
            r"cmd\s+(.+)",
            r"command\s+(.+)",
            r"terminal\s+(.+)",
            r"shell\s+(.+)",
            r"run\s+(.+)",
            r"do\s+(.+)",
            r"show\s+(.+)",
            r"display\s+(.+)",
            r"get\s+(.+)",
            r"check\s+(.+)",
            r"scan\s+(.+)",
            r"clean\s+(.+)",
            r"reset\s+(.+)",
            r"flush\s+(.+)",
            r"ping\s+(.+)",
            r"tracert\s+(.+)",
            r"nslookup\s+(.+)",
            r"copy\s+(.+)",
            r"move\s+(.+)",
            r"delete\s+(.+)",
            r"del\s+(.+)",
            r"mkdir\s+(.+)",
            r"rmdir\s+(.+)",
            r"cd\s+(.+)",
            r"dir\s+(.+)",
            r"list\s+(.+)",
            r"show\s+(.+)",
            r"tree\s+(.+)",
            r"type\s+(.+)",
            r"find\s+(.+)",
            r"findstr\s+(.+)",
            r"sort\s+(.+)",
            r"echo\s+(.+)",
            # File and folder creation patterns
            r"create\s+(?:a\s+)?(?:new\s+)?folder\s+(?:called\s+)?(.+)",
            r"create\s+(?:a\s+)?(?:new\s+)?directory\s+(?:called\s+)?(.+)",
            r"make\s+(?:a\s+)?(?:new\s+)?folder\s+(?:called\s+)?(.+)",
            r"make\s+(?:a\s+)?(?:new\s+)?directory\s+(?:called\s+)?(.+)",
            r"new\s+folder\s+(?:called\s+)?(.+)",
            r"new\s+directory\s+(?:called\s+)?(.+)",
            r"create\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+)?(.+)",
            r"make\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+)?(.+)",
            r"new\s+file\s+(?:called\s+)?(.+)",
            r"touch\s+(.+)",
            # File operations
            r"delete\s+(?:file\s+)?(.+)",
            r"remove\s+(?:file\s+)?(.+)",
            r"copy\s+(?:file\s+)?(.+)",
            r"move\s+(?:file\s+)?(.+)",
            r"rename\s+(?:file\s+)?(.+)",
            r"list\s+(?:files?\s+)?(?:in\s+)?(.+)",
            r"show\s+(?:files?\s+)?(?:in\s+)?(.+)",
            r"dir\s+(.+)",
            r"ls\s+(.+)",
            r"cls",
            r"clear",
            r"help",
            r"ver",
            r"whoami",
            r"hostname",
            r"date",
            r"time"
        ]
        
        for pattern in command_patterns:
            if pattern in query_lower:
                if pattern in ["cls", "clear", "help", "ver", "whoami", "hostname", "date", "time"]:
                    return pattern
                else:
                    match = re.search(pattern, query_lower)
                    if match:
                        return match.group(1).strip()
        
        return None
    
    def install_package(self, query: str) -> str:
        """Install a package based on user query"""
        try:
            package_name = self._extract_package_name(query)
            if not package_name:
                return "I couldn't identify what package you want to install. Please be more specific."
            
            manager, command = self._get_package_manager_command(package_name)
            if not manager or not command:
                return f"I don't have a suitable package manager available to install {package_name}. Available managers: {', '.join(self.available_managers)}"
            
            print(f"🔧 Installing {package_name} using {manager}: {command}")
            
            # Run the installation command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return f"✅ Successfully installed {package_name} using {manager}."
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return f"❌ Failed to install {package_name} using {manager}. Error: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return f"⏰ Installation of {package_name} timed out. It might still be running in the background."
        except Exception as e:
            return f"❌ Error installing package: {str(e)}"
    
    def run_system_command(self, query: str) -> str:
        """Run a system command"""
        try:
            command_to_run = self._extract_system_command(query)
            if not command_to_run:
                return "I couldn't identify what system command you want me to run. Please be more specific."
            
            print(f"🔧 Running system command: {command_to_run}")
            
            # Run the command
            result = subprocess.run(
                command_to_run,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    return f"✅ System command executed successfully:\n{output}"
                else:
                    return f"✅ System command '{command_to_run}' executed successfully."
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return f"❌ System command failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return f"⏰ System command timed out after 60 seconds."
        except Exception as e:
            return f"❌ Error running system command: {str(e)}"
    
    def run_command(self, query: str) -> str:
        """Run a general command line command"""
        try:
            # Extract command from query
            # Enhanced patterns for command extraction
            patterns = [
                r"run\s+(?:command\s+)?(.+)",
                r"execute\s+(.+)",
                r"cmd\s+(.+)",
                r"command\s+(.+)",
                r"terminal\s+(.+)",
                r"shell\s+(.+)",
                r"run\s+(.+)",
                r"do\s+(.+)"
            ]
            
            command_to_run = None
            for pattern in patterns:
                match = re.search(pattern, query.lower())
                if match:
                    command_to_run = match.group(1).strip()
                    break
            
            if not command_to_run:
                return "I couldn't identify what command you want me to run. Please be more specific."
            
            print(f"🔧 Running command: {command_to_run}")
            
            # Run the command
            result = subprocess.run(
                command_to_run,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    return f"✅ Command executed successfully:\n{output}"
                else:
                    return f"✅ Command '{command_to_run}' executed successfully."
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return f"❌ Command failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return f"⏰ Command timed out after 60 seconds."
        except Exception as e:
            return f"❌ Error running command: {str(e)}"
    
    def create_file_or_folder(self, query: str) -> str:
        """Create files and folders based on user query"""
        try:
            import os
            
            # Extract the name from the query
            name = None
            
            # Check for folder creation patterns
            folder_patterns = [
                r"create\s+(?:a\s+)?(?:new\s+)?folder\s+(?:called\s+)?(.+)",
                r"create\s+(?:a\s+)?(?:new\s+)?directory\s+(?:called\s+)?(.+)",
                r"make\s+(?:a\s+)?(?:new\s+)?folder\s+(?:called\s+)?(.+)",
                r"make\s+(?:a\s+)?(?:new\s+)?directory\s+(?:called\s+)?(.+)",
                r"new\s+folder\s+(?:called\s+)?(.+)",
                r"new\s+directory\s+(?:called\s+)?(.+)"
            ]
            
            # Check for file creation patterns
            file_patterns = [
                r"create\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+)?(.+)",
                r"make\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+)?(.+)",
                r"new\s+file\s+(?:called\s+)?(.+)",
                r"touch\s+(.+)"
            ]
            
            # Check if it's a folder creation request
            for pattern in folder_patterns:
                match = re.search(pattern, query.lower())
                if match:
                    name = match.group(1).strip()
                    if name:
                        # Create the folder
                        os.makedirs(name, exist_ok=True)
                        return f"✅ Successfully created folder: '{name}'"
            
            # Check if it's a file creation request
            for pattern in file_patterns:
                match = re.search(pattern, query.lower())
                if match:
                    name = match.group(1).strip()
                    if name:
                        # Create the file (touch equivalent)
                        with open(name, 'a') as f:
                            pass  # Just create the file
                        return f"✅ Successfully created file: '{name}'"
            
            return "I couldn't identify what file or folder you want to create. Please be more specific."
            
        except Exception as e:
            return f"❌ Error creating file/folder: {str(e)}"
    
    def handle_command_request(self, query: str) -> str:
        """Main handler for command line automation requests"""
        query_lower = query.lower()
        
        # Check if it's an installation request
        install_keywords = ["install", "get", "download", "add", "setup", "install git", "install python", "install chrome", "install firefox"]
        if any(keyword in query_lower for keyword in install_keywords):
            return self.install_package(query)
        
        # Check if it's a file/folder creation request
        file_folder_keywords = [
            "create folder", "create file", "make folder", "make file", 
            "new folder", "new file", "new directory", "create directory",
            "touch"
        ]
        if any(keyword in query_lower for keyword in file_folder_keywords):
            return self.create_file_or_folder(query)
        
        # Check if it's a system command request
        system_command_keywords = [
            "system info", "disk space", "memory info", "cpu info", "network info", 
            "processes", "services", "shutdown", "restart", "sleep", "hibernate",
            "clean temp", "disk cleanup", "defrag", "check disk", "sfc scan",
            "windows update", "firewall status", "network reset", "dns flush",
            "ping", "tracert", "nslookup", "whoami", "hostname", "date", "time",
            "dir", "list files", "tree", "copy", "move", "delete", "mkdir", "rmdir",
            "cd", "echo", "type", "find", "sort", "cls", "clear", "help", "ver"
        ]
        if any(keyword in query_lower for keyword in system_command_keywords):
            return self.run_system_command(query)
        
        # Check if it's a general command request
        command_keywords = ["run command", "execute", "cmd", "terminal", "shell", "run", "do"]
        if any(keyword in query_lower for keyword in command_keywords):
            return self.run_command(query)
        
        # Check for specific package mentions
        for package in self.package_mappings.keys():
            if package in query_lower and any(word in query_lower for word in ["install", "get", "download", "add", "setup"]):
                return self.install_package(query)
        
        return "I'm not sure what command line operation you want me to perform. Please be more specific."

# Global instance
command_line_automation = CommandLineAutomation()

def handle_command_line_request(query: str) -> str:
    """Main function to handle command line automation requests"""
    return command_line_automation.handle_command_request(query)

# Standalone file explorer automation functions
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

def open_file_explorer_at_path(path):
    """Open File Explorer at specific path"""
    try:
        subprocess.run(["explorer", path], shell=True)
        return f"Opening File Explorer at: {path}"
    except Exception as e:
        print(f"File Explorer path command failed: {e}")
        return f"Failed to open File Explorer at: {path}"
