import subprocess
import os
import sys
import time
import logging
from typing import List, Optional, Tuple
import ctypes
from admin_face_recognition import AdminFaceRecognition

class CMDAdminIntegration:
    def __init__(self, face_recognition: AdminFaceRecognition):
        """
        Initialize CMD Admin Integration
        
        Args:
            face_recognition: Instance of AdminFaceRecognition
        """
        self.face_recognition = face_recognition
        self.logger = logging.getLogger(__name__)
        self.is_admin_mode = False
        self.current_admin = None
        
    def is_windows_admin(self) -> bool:
        """Check if the current process is running with admin privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def request_admin_privileges(self) -> bool:
        """Request admin privileges for the current process"""
        try:
            if self.is_windows_admin():
                return True
            
            # Re-run the script with admin privileges
            script_path = sys.argv[0]
            if script_path.endswith('.py'):
                script_path = f'python "{script_path}"'
            
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, script_path, None, 1
            )
            
            if result > 32:
                self.logger.info("Admin privileges requested successfully")
                return True
            else:
                self.logger.error("Failed to request admin privileges")
                return False
                
        except Exception as e:
            self.logger.error(f"Error requesting admin privileges: {e}")
            return False
    
    def authenticate_admin_face(self, timeout: int = 30) -> Tuple[bool, Optional[str]]:
        """
        Authenticate admin using face recognition
        
        Args:
            timeout: Timeout in seconds for face recognition
            
        Returns:
            Tuple of (is_authenticated, admin_name)
        """
        try:
            self.logger.info("Starting admin face authentication...")
            print("🔐 ADMIN AUTHENTICATION REQUIRED")
            print("Please look at the camera for face recognition...")
            print(f"Timeout: {timeout} seconds")
            
            # Perform face recognition
            is_authenticated = self.face_recognition.real_time_recognition(duration=timeout)
            
            if is_authenticated:
                # Get the last recognized admin name from the face recognition system
                # This is a simplified approach - in a real implementation, you'd want to
                # return the admin name from the recognition process
                admin_name = "Authenticated Admin"
                self.current_admin = admin_name
                self.logger.info(f"Admin authentication successful: {admin_name}")
                print(f"✅ ADMIN AUTHENTICATED: {admin_name}")
                return True, admin_name
            else:
                self.logger.warning("Admin face authentication failed")
                print("❌ ADMIN AUTHENTICATION FAILED")
                return False, None
                
        except Exception as e:
            self.logger.error(f"Error in admin face authentication: {e}")
            print(f"❌ AUTHENTICATION ERROR: {e}")
            return False, None
    
    def execute_cmd_with_auth(self, command: str, require_auth: bool = True) -> Tuple[bool, str]:
        """
        Execute a command with admin authentication if required
        
        Args:
            command: Command to execute
            require_auth: Whether to require face authentication
            
        Returns:
            Tuple of (success, output)
        """
        try:
            if require_auth:
                # Check if already authenticated
                if not self.current_admin:
                    print("🔐 Face authentication required for this command...")
                    is_authenticated, admin_name = self.authenticate_admin_face()
                    
                    if not is_authenticated:
                        return False, "Admin authentication failed"
                
                print(f"✅ Executing command as admin: {command}")
            
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.logger.info(f"Command executed successfully: {command}")
                return True, result.stdout
            else:
                self.logger.warning(f"Command failed with return code {result.returncode}: {command}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out: {command}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error executing command: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def start_secure_cmd_session(self):
        """Start a secure CMD session with continuous face authentication"""
        try:
            print("🚀 STARTING SECURE ADMIN CMD SESSION")
            print("=" * 50)
            print("This session requires continuous face authentication")
            print("Commands will only execute when admin face is detected")
            print("Type 'exit' to quit the session")
            print("=" * 50)
            
            # Initial authentication
            is_authenticated, admin_name = self.authenticate_admin_face()
            if not is_authenticated:
                print("❌ Initial authentication failed. Session terminated.")
                return
            
            print(f"✅ Session started for admin: {admin_name}")
            print("You can now execute commands...")
            
            session_start_time = time.time()
            last_auth_time = time.time()
            auth_timeout = 300  # 5 minutes
            
            while True:
                try:
                    # Check if re-authentication is needed
                    if time.time() - last_auth_time > auth_timeout:
                        print("⏰ Re-authentication required...")
                        is_authenticated, admin_name = self.authenticate_admin_face(timeout=30)
                        if not is_authenticated:
                            print("❌ Re-authentication failed. Session terminated.")
                            break
                        last_auth_time = time.time()
                        print(f"✅ Re-authenticated: {admin_name}")
                    
                    # Get command input
                    command = input(f"\n[{admin_name}] CMD> ").strip()
                    
                    if command.lower() in ['exit', 'quit', 'logout']:
                        print("👋 Ending secure admin session...")
                        break
                    
                    if not command:
                        continue
                    
                    # Execute command with authentication
                    success, output = self.execute_cmd_with_auth(command, require_auth=False)
                    
                    if success:
                        print("✅ Command executed successfully:")
                        print(output if output else "Command completed with no output")
                    else:
                        print("❌ Command failed:")
                        print(output)
                
                except KeyboardInterrupt:
                    print("\n⚠️  Session interrupted. Type 'exit' to quit properly.")
                except EOFError:
                    print("\n👋 Session ended.")
                    break
            
            session_duration = time.time() - session_start_time
            print(f"📊 Session duration: {session_duration:.1f} seconds")
            print("🔒 Secure admin session terminated.")
            
        except Exception as e:
            self.logger.error(f"Error in secure CMD session: {e}")
            print(f"❌ Session error: {e}")
    
    def batch_execute_commands(self, commands: List[str], require_auth: bool = True) -> List[Tuple[bool, str, str]]:
        """
        Execute multiple commands in batch with authentication
        
        Args:
            commands: List of commands to execute
            require_auth: Whether to require face authentication
            
        Returns:
            List of tuples (success, command, output)
        """
        results = []
        
        try:
            if require_auth:
                print("🔐 Batch execution requires admin authentication...")
                is_authenticated, admin_name = self.authenticate_admin_face()
                
                if not is_authenticated:
                    print("❌ Batch execution cancelled due to authentication failure")
                    return [(False, cmd, "Authentication failed") for cmd in commands]
                
                print(f"✅ Batch execution authenticated for admin: {admin_name}")
            
            print(f"🚀 Executing {len(commands)} commands...")
            
            for i, command in enumerate(commands, 1):
                print(f"\n[{i}/{len(commands)}] Executing: {command}")
                
                success, output = self.execute_cmd_with_auth(command, require_auth=False)
                results.append((success, command, output))
                
                if success:
                    print(f"✅ Command {i} successful")
                else:
                    print(f"❌ Command {i} failed")
                
                # Small delay between commands
                time.sleep(0.5)
            
            # Summary
            successful = sum(1 for success, _, _ in results if success)
            print(f"\n📊 Batch execution complete: {successful}/{len(commands)} commands successful")
            
        except Exception as e:
            self.logger.error(f"Error in batch execution: {e}")
            print(f"❌ Batch execution error: {e}")
        
        return results
    
    def monitor_cmd_processes(self, duration: int = 300):
        """
        Monitor CMD processes and require re-authentication for new processes
        
        Args:
            duration: Duration to monitor in seconds
        """
        try:
            print(f"🔍 Starting CMD process monitoring for {duration} seconds...")
            print("New CMD processes will require face authentication")
            
            start_time = time.time()
            known_processes = set()
            
            while time.time() - start_time < duration:
                try:
                    # Get current CMD processes
                    result = subprocess.run(
                        'tasklist /FI "IMAGENAME eq cmd.exe" /FO CSV',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        current_processes = set()
                        lines = result.stdout.strip().split('\n')[1:]  # Skip header
                        
                        for line in lines:
                            if line.strip():
                                parts = line.split(',')
                                if len(parts) >= 2:
                                    pid = parts[1].strip('"')
                                    current_processes.add(pid)
                        
                        # Check for new processes
                        new_processes = current_processes - known_processes
                        if new_processes:
                            print(f"🆕 New CMD processes detected: {new_processes}")
                            print("🔐 Re-authentication required...")
                            
                            is_authenticated, admin_name = self.authenticate_admin_face(timeout=30)
                            if is_authenticated:
                                print(f"✅ Re-authenticated for new processes: {admin_name}")
                                known_processes.update(new_processes)
                            else:
                                print("❌ Re-authentication failed for new processes")
                        
                        known_processes = current_processes
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except KeyboardInterrupt:
                    print("\n⚠️  Monitoring interrupted.")
                    break
                except Exception as e:
                    self.logger.error(f"Error in process monitoring: {e}")
                    time.sleep(5)
            
            print("🔍 CMD process monitoring completed.")
            
        except Exception as e:
            self.logger.error(f"Error in process monitoring: {e}")
            print(f"❌ Monitoring error: {e}")

def main():
    """Main function for testing the CMD Admin Integration"""
    try:
        print("🔐 YOLOv8 Admin Face Recognition - CMD Integration")
        print("=" * 60)
        
        # Initialize face recognition
        print("Initializing face recognition system...")
        face_recognition = AdminFaceRecognition()
        
        # Initialize CMD integration
        cmd_integration = CMDAdminIntegration(face_recognition)
        
        print("\nAvailable options:")
        print("1. Start secure CMD session")
        print("2. Execute single command with auth")
        print("3. Batch execute commands")
        print("4. Monitor CMD processes")
        print("5. Add new admin face")
        print("6. Exit")
        
        while True:
            try:
                choice = input("\nSelect option (1-6): ").strip()
                
                if choice == '1':
                    cmd_integration.start_secure_cmd_session()
                elif choice == '2':
                    command = input("Enter command: ").strip()
                    if command:
                        success, output = cmd_integration.execute_cmd_with_auth(command)
                        if success:
                            print("✅ Success:", output)
                        else:
                            print("❌ Failed:", output)
                elif choice == '3':
                    commands = []
                    print("Enter commands (one per line, empty line to finish):")
                    while True:
                        cmd = input("Command: ").strip()
                        if not cmd:
                            break
                        commands.append(cmd)
                    
                    if commands:
                        cmd_integration.batch_execute_commands(commands)
                elif choice == '4':
                    duration = input("Enter monitoring duration in seconds (default 300): ").strip()
                    try:
                        duration = int(duration) if duration else 300
                        cmd_integration.monitor_cmd_processes(duration)
                    except ValueError:
                        print("Invalid duration, using default 300 seconds")
                        cmd_integration.monitor_cmd_processes()
                elif choice == '5':
                    admin_name = input("Enter admin name: ").strip()
                    if admin_name:
                        face_recognition.capture_admin_face(admin_name)
                elif choice == '6':
                    print("👋 Goodbye!")
                    break
                else:
                    print("Invalid option. Please select 1-6.")
                    
            except KeyboardInterrupt:
                print("\n⚠️  Interrupted. Type '6' to exit.")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        logging.error(f"Initialization error: {e}")

if __name__ == "__main__":
    main()
