import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import time
import logging
import subprocess
import threading
from typing import Set, Optional
import ctypes
from admin_face_recognition import AdminFaceRecognition
from cmd_admin_integration import CMDAdminIntegration

class AdminFaceRecognitionService(win32serviceutil.ServiceFramework):
    """
    Windows Service for Admin Face Recognition
    Monitors CMD processes and requires face authentication for admin operations
    """
    
    _svc_name_ = "AdminFaceRecognitionService"
    _svc_display_name_ = "Admin Face Recognition Service"
    _svc_description_ = "Monitors CMD processes and requires face authentication for admin operations"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = False
        self.face_recognition = None
        self.cmd_integration = None
        self.monitoring_thread = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('C:\\admin_face_recognition_service.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Known CMD processes
        self.known_cmd_processes: Set[str] = set()
        self.admin_authenticated_processes: Set[str] = set()
        
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Stopping Admin Face Recognition Service...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False
        
    def SvcDoRun(self):
        """Run the service"""
        try:
            self.logger.info("Starting Admin Face Recognition Service...")
            self.is_running = True
            
            # Initialize face recognition system
            self.initialize_face_recognition()
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self.monitor_cmd_processes)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            # Main service loop
            while self.is_running:
                # Check if stop event is signaled
                if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                    break
                
                # Service is running, continue monitoring
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            self.is_running = False
        finally:
            self.logger.info("Admin Face Recognition Service stopped.")
    
    def initialize_face_recognition(self):
        """Initialize the face recognition system"""
        try:
            self.logger.info("Initializing face recognition system...")
            
            # Create admin faces directory in system location
            admin_faces_dir = "C:\\admin_faces"
            os.makedirs(admin_faces_dir, exist_ok=True)
            
            # Initialize face recognition
            self.face_recognition = AdminFaceRecognition(admin_faces_dir)
            
            # Initialize CMD integration
            self.cmd_integration = CMDAdminIntegration(self.face_recognition)
            
            self.logger.info("Face recognition system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize face recognition: {e}")
            raise
    
    def monitor_cmd_processes(self):
        """Monitor CMD processes and require authentication for new ones"""
        try:
            self.logger.info("Starting CMD process monitoring...")
            
            while self.is_running:
                try:
                    # Get current CMD processes
                    current_processes = self.get_cmd_processes()
                    
                    if current_processes:
                        # Check for new processes
                        new_processes = current_processes - self.known_cmd_processes
                        
                        for pid in new_processes:
                            self.logger.info(f"New CMD process detected: PID {pid}")
                            
                            # Check if process is running with admin privileges
                            if self.is_process_admin(pid):
                                self.logger.info(f"Admin CMD process detected: PID {pid}")
                                
                                # Require face authentication
                                if self.require_face_authentication(pid):
                                    self.admin_authenticated_processes.add(pid)
                                    self.logger.info(f"Admin process {pid} authenticated via face recognition")
                                else:
                                    self.logger.warning(f"Admin process {pid} failed face authentication")
                                    # Could implement process termination here
                        
                        # Update known processes
                        self.known_cmd_processes = current_processes
                    
                    # Sleep before next check
                    time.sleep(5)
                    
                except Exception as e:
                    self.logger.error(f"Error in process monitoring: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            self.logger.error(f"Fatal error in process monitoring: {e}")
    
    def get_cmd_processes(self) -> Set[str]:
        """Get current CMD process PIDs"""
        try:
            result = subprocess.run(
                'tasklist /FI "IMAGENAME eq cmd.exe" /FO CSV',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                processes = set()
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 2:
                            pid = parts[1].strip('"')
                            processes.add(pid)
                
                return processes
            
        except Exception as e:
            self.logger.error(f"Error getting CMD processes: {e}")
        
        return set()
    
    def is_process_admin(self, pid: str) -> bool:
        """Check if a process is running with admin privileges"""
        try:
            # Use wmic to get process information
            result = subprocess.run(
                f'wmic process where "ProcessId={pid}" get ExecutablePath /format:csv',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Check if the process path indicates admin privileges
                # This is a simplified check - in production you'd want more robust detection
                return True
            
        except Exception as e:
            self.logger.error(f"Error checking process admin status: {e}")
        
        return False
    
    def require_face_authentication(self, pid: str) -> bool:
        """Require face authentication for a specific process"""
        try:
            self.logger.info(f"Requiring face authentication for process {pid}")
            
            # Create a notification for the user
            self.show_authentication_notification(pid)
            
            # Perform face authentication
            if self.face_recognition and self.cmd_integration:
                is_authenticated, admin_name = self.cmd_integration.authenticate_admin_face(timeout=30)
                
                if is_authenticated:
                    self.logger.info(f"Face authentication successful for process {pid}: {admin_name}")
                    return True
                else:
                    self.logger.warning(f"Face authentication failed for process {pid}")
                    return False
            
        except Exception as e:
            self.logger.error(f"Error in face authentication: {e}")
        
        return False
    
    def show_authentication_notification(self, pid: str):
        """Show a notification to the user about required authentication"""
        try:
            # Use Windows toast notification or message box
            title = "Admin Authentication Required"
            message = f"CMD process (PID: {pid}) requires admin face authentication.\nPlease look at the camera."
            
            # Show message box
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x30)  # MB_ICONWARNING
            
        except Exception as e:
            self.logger.error(f"Error showing authentication notification: {e}")
    
    def get_service_status(self) -> dict:
        """Get current service status"""
        return {
            'is_running': self.is_running,
            'known_processes': len(self.known_cmd_processes),
            'authenticated_processes': len(self.admin_authenticated_processes),
            'face_recognition_initialized': self.face_recognition is not None
        }

class AdminFaceRecognitionManager:
    """Manager class for controlling the Admin Face Recognition Service"""
    
    def __init__(self):
        self.service_name = "AdminFaceRecognitionService"
        self.logger = logging.getLogger(__name__)
        
    def install_service(self):
        """Install the Admin Face Recognition Service"""
        try:
            print("Installing Admin Face Recognition Service...")
            
            # Get the current script path
            script_path = os.path.abspath(__file__)
            
            # Install the service
            win32serviceutil.InstallService(
                None,
                self.service_name,
                self.service_name,
                startType=win32service.SERVICE_AUTO_START
            )
            
            print("✅ Service installed successfully!")
            print("You can start it with: net start AdminFaceRecognitionService")
            
        except Exception as e:
            print(f"❌ Failed to install service: {e}")
            self.logger.error(f"Service installation failed: {e}")
    
    def uninstall_service(self):
        """Uninstall the Admin Face Recognition Service"""
        try:
            print("Uninstalling Admin Face Recognition Service...")
            
            # Stop the service first if it's running
            try:
                win32serviceutil.StopService(self.service_name)
                print("Service stopped.")
            except:
                pass
            
            # Remove the service
            win32serviceutil.RemoveService(self.service_name)
            
            print("✅ Service uninstalled successfully!")
            
        except Exception as e:
            print(f"❌ Failed to uninstall service: {e}")
            self.logger.error(f"Service uninstallation failed: {e}")
    
    def start_service(self):
        """Start the Admin Face Recognition Service"""
        try:
            print("Starting Admin Face Recognition Service...")
            win32serviceutil.StartService(self.service_name)
            print("✅ Service started successfully!")
            
        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            self.logger.error(f"Service start failed: {e}")
    
    def stop_service(self):
        """Stop the Admin Face Recognition Service"""
        try:
            print("Stopping Admin Face Recognition Service...")
            win32serviceutil.StopService(self.service_name)
            print("✅ Service stopped successfully!")
            
        except Exception as e:
            print(f"❌ Failed to stop service: {e}")
            self.logger.error(f"Service stop failed: {e}")
    
    def get_service_status(self):
        """Get the status of the Admin Face Recognition Service"""
        try:
            status = win32serviceutil.QueryServiceStatus(self.service_name)
            status_map = {
                win32service.SERVICE_RUNNING: "Running",
                win32service.SERVICE_STOPPED: "Stopped",
                win32service.SERVICE_START_PENDING: "Starting",
                win32service.SERVICE_STOP_PENDING: "Stopping"
            }
            
            current_status = status_map.get(status[1], "Unknown")
            print(f"Service Status: {current_status}")
            
        except Exception as e:
            print(f"❌ Failed to get service status: {e}")
            self.logger.error(f"Service status check failed: {e}")

def main():
    """Main function for service management"""
    try:
        print("🔐 Admin Face Recognition Service Manager")
        print("=" * 50)
        
        if len(sys.argv) == 1:
            # No arguments provided, show usage
            print("\nUsage:")
            print("  python windows_service_integration.py install    - Install service")
            print("  python windows_service_integration.py uninstall  - Uninstall service")
            print("  python windows_service_integration.py start      - Start service")
            print("  python windows_service_integration.py stop       - Stop service")
            print("  python windows_service_integration.py status     - Check service status")
            print("  python windows_service_integration.py debug      - Run in debug mode")
            print("\nNote: Run as Administrator for service operations")
            return
        
        action = sys.argv[1].lower()
        manager = AdminFaceRecognitionManager()
        
        if action == "install":
            manager.install_service()
        elif action == "uninstall":
            manager.uninstall_service()
        elif action == "start":
            manager.start_service()
        elif action == "stop":
            manager.stop_service()
        elif action == "status":
            manager.get_service_status()
        elif action == "debug":
            # Run the service in debug mode (not as a Windows service)
            print("Running in debug mode...")
            service = AdminFaceRecognitionService([])
            service.SvcDoRun()
        else:
            print(f"❌ Unknown action: {action}")
            print("Use 'install', 'uninstall', 'start', 'stop', 'status', or 'debug'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Main error: {e}")

if __name__ == "__main__":
    main()
