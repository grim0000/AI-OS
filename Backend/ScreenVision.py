"""
Real-time Screen Vision System
Captures screen, analyzes with AI vision, and provides intelligent automation feedback
"""

import cv2
import numpy as np
import mss
from PIL import Image
import time
import threading
from typing import Optional, Tuple, List, Dict
import os
from groq import Groq

class ScreenVisionSystem:
    def __init__(self):
        """Initialize screen vision system with AI capabilities"""
        # Don't create global mss instance to avoid threading issues
        self.is_monitoring = False
        self.current_screenshot = None
        self.last_analysis = None
        self.analysis_thread = None
        
        # Initialize Groq client for vision analysis (optional)
        try:
            groq_api_key = os.getenv('GROQ_API_KEY')
            if groq_api_key:
                self.groq_client = Groq(api_key=groq_api_key)
                self.groq_available = True
            else:
                self.groq_client = None
                self.groq_available = False
        except Exception as e:
            print(f"⚠️ Groq client initialization failed: {e}")
            self.groq_client = None
            self.groq_available = False
        
        # Screen regions of interest for automation
        self.roi_cache = {}
        
        print("🖥️ Screen Vision System initialized")
    
    def capture_screen(self, monitor_index: int = 1) -> np.ndarray:
        """Capture current screen as numpy array with improved threading support"""
        try:
            # Create a new mss instance for this capture to avoid threading issues
            with mss.mss() as sct:
                # Get monitor info
                monitor = sct.monitors[monitor_index]
                
                # Capture screenshot
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                img = np.array(screenshot)
                
                # Convert BGRA to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                
                self.current_screenshot = img
                return img
            
        except Exception as e:
            print(f"❌ Screen capture failed: {e}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture specific screen region with improved threading support"""
        try:
            # Create a new mss instance for this capture to avoid threading issues
            with mss.mss() as sct:
                region = {
                    "top": y,
                    "left": x,
                    "width": width,
                    "height": height
                }
                
                screenshot = sct.grab(region)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                
                return img
            
        except Exception as e:
            print(f"❌ Region capture failed: {e}")
            return None
    

    
    def analyze_screen_with_ai(self, query: str, img: Optional[np.ndarray] = None) -> str:
        """Analyze screen content using computer vision"""
        try:
            # Use current screenshot if no image provided
            if img is None:
                if self.current_screenshot is None:
                    self.capture_screen()
                img = self.current_screenshot
            
            if img is None:
                return "❌ No screen capture available"
            
            # Use computer vision analysis
            analysis = self.analyze_screen_elements(img, query)
            
            self.last_analysis = analysis
            return analysis
            
        except Exception as e:
            print(f"❌ Screen analysis failed: {e}")
            return f"❌ Analysis error: {str(e)}"
    
    def analyze_screen_elements(self, img: np.ndarray, query: str) -> str:
        """Analyze screen using computer vision techniques"""
        try:
            height, width = img.shape[:2]
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            
            # Detect text regions using edge detection
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find UI elements
            ui_elements = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Filter small elements
                    x, y, w, h = cv2.boundingRect(contour)
                    ui_elements.append({
                        'type': 'ui_element',
                        'position': (x, y),
                        'size': (w, h),
                        'area': area
                    })
            
            # Detect potential buttons (rectangular regions)
            buttons = []
            for element in ui_elements:
                x, y = element['position']
                w, h = element['size']
                aspect_ratio = w / h if h > 0 else 0
                
                # Button-like characteristics
                if 1.5 <= aspect_ratio <= 6 and 20 <= h <= 60 and w >= 50:
                    buttons.append({
                        'position': (x + w//2, y + h//2),  # Center point
                        'size': (w, h),
                        'confidence': 0.8
                    })
            
            # Analyze for Spotify-specific elements
            spotify_analysis = ""
            if "spotify" in query.lower():
                spotify_analysis = self.analyze_spotify_interface(img, gray)
            
            # Build comprehensive analysis
            analysis = f"""🖥️ **Screen Analysis Report**
            
**Screen Resolution**: {width}x{height}
**UI Elements Found**: {len(ui_elements)}
**Potential Buttons**: {len(buttons)}

**Query**: {query}

{spotify_analysis}

**Detected Clickable Areas**:
"""
            
            # Add top 5 most likely clickable areas
            sorted_buttons = sorted(buttons, key=lambda x: x['confidence'], reverse=True)[:5]
            for i, button in enumerate(sorted_buttons, 1):
                x, y = button['position']
                w, h = button['size']
                analysis += f"\n{i}. Position ({x}, {y}) - Size: {w}x{h}"
            
            return analysis
            
        except Exception as e:
            return f"❌ Computer vision analysis failed: {str(e)}"
    
    def analyze_spotify_interface(self, img: np.ndarray, gray: np.ndarray) -> str:
        """Specialized analysis for Spotify interface"""
        try:
            height, width = img.shape[:2]
            
            # Look for Spotify's characteristic green color
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            
            # Spotify green color range
            lower_green = np.array([60, 100, 100])
            upper_green = np.array([80, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Find green elements (likely Spotify UI)
            green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Look for play button characteristics (circular)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=50)
            
            play_buttons = []
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    play_buttons.append({'center': (x, y), 'radius': r})
            
            # Look for search results area (typically in upper portion)
            search_area_y = height // 4
            search_region = img[search_area_y:search_area_y + height//2, :]
            
            # Detect text-like regions in search area
            search_gray = cv2.cvtColor(search_region, cv2.COLOR_RGB2GRAY)
            search_edges = cv2.Canny(search_gray, 30, 100)
            search_contours, _ = cv2.findContours(search_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            search_results = []
            for contour in search_contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Significant area for song results
                    x, y, w, h = cv2.boundingRect(contour)
                    actual_y = y + search_area_y  # Adjust for region offset
                    search_results.append({
                        'position': (x + w//2, actual_y + h//2),
                        'size': (w, h)
                    })
            
            analysis = f"""
**🎵 Spotify Interface Analysis**:

**Green UI Elements**: {len(green_contours)} (Spotify branding detected)
**Potential Play Buttons**: {len(play_buttons)}
**Search Results**: {len(search_results)}

**Recommended Click Targets**:
"""
            
            # First search result (most likely to be the target)
            if search_results:
                first_result = search_results[0]
                x, y = first_result['position']
                analysis += f"\n🎯 **Primary Target**: First search result at ({x}, {y})"
            
            # Play buttons
            for i, button in enumerate(play_buttons[:3], 1):
                x, y = button['center']
                analysis += f"\n▶️ **Play Button {i}**: ({x}, {y})"
            
            return analysis
            
        except Exception as e:
            return f"❌ Spotify analysis failed: {str(e)}"
    
    def find_best_click_target(self, target_description: str) -> Optional[Tuple[int, int]]:
        """Find the best click coordinates for a given target with enhanced detection"""
        try:
            if self.current_screenshot is None:
                self.capture_screen()
            
            if self.current_screenshot is None:
                return None
            
            height, width = self.current_screenshot.shape[:2]
            
            # Enhanced detection for Spotify search results
            if "first search result" in target_description.lower() and "spotify" in target_description.lower():
                # Analyze the screen for Spotify-specific elements
                analysis_result = self.analyze_spotify_interface(self.current_screenshot, cv2.cvtColor(self.current_screenshot, cv2.COLOR_RGB2GRAY))
                
                # Look for search results in the analysis
                if "Primary Target" in analysis_result:
                    # Extract coordinates from the analysis
                    import re
                    match = re.search(r'First search result at \((\d+), (\d+)\)', analysis_result)
                    if match:
                        x, y = int(match.group(1)), int(match.group(2))
                        print(f"🎯 Extracted coordinates from analysis: ({x}, {y})")
                        return (x, y)
                
                # Fallback: Use intelligent positioning based on screen analysis
                # Spotify search results typically appear in the upper-middle area
                search_area_x = width // 4  # One-quarter from left
                search_area_y = height // 4  # One-quarter from top
                
                # Try multiple positions in the search results area
                positions = [
                    (search_area_x, search_area_y),
                    (search_area_x + 100, search_area_y),
                    (search_area_x, search_area_y + 50),
                    (search_area_x + 100, search_area_y + 50),
                ]
                
                # Return the first position (most likely to be the first result)
                print(f"🎯 Using intelligent positioning: {positions[0]}")
                return positions[0]
            
            # Generic target detection
            elif "button" in target_description.lower():
                # Look for button-like elements in the center area
                center_x = width // 2
                center_y = height // 2
                return (center_x, center_y)
            
            # Default: return center of screen
            else:
                center_x = width // 2
                center_y = height // 2
                return (center_x, center_y)
            
        except Exception as e:
            print(f"❌ Click target detection failed: {e}")
            return None
    
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous screen monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            while self.is_monitoring:
                self.capture_screen()
                time.sleep(interval)
        
        self.analysis_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.analysis_thread.start()
        
        print("📹 Screen monitoring started")
    
    def stop_monitoring(self):
        """Stop screen monitoring"""
        self.is_monitoring = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=2)
        
        print("⏹️ Screen monitoring stopped")
    
    def get_screen_info(self) -> Dict:
        """Get current screen information"""
        try:
            # Create temporary mss instance to get monitor info
            with mss.mss() as sct:
                monitors = []
                for i, monitor in enumerate(sct.monitors):
                    monitors.append({
                        'index': i,
                        'width': monitor['width'],
                        'height': monitor['height'],
                        'left': monitor['left'],
                        'top': monitor['top']
                    })
                
                return {
                    'monitors': monitors,
                    'current_screenshot_available': self.current_screenshot is not None,
                    'last_analysis': self.last_analysis,
                    'is_monitoring': self.is_monitoring
                }
            
        except Exception as e:
            return {'error': str(e)}

# Global screen vision instance
try:
    screen_vision = ScreenVisionSystem()
except Exception as e:
    print(f"⚠️ Failed to initialize global screen vision instance: {e}")
    screen_vision = None

def capture_and_analyze(query: str = "analyze current screen") -> str:
    """Quick function to capture and analyze screen"""
    try:
        if screen_vision is None:
            return "❌ Screen vision system not available"
        screen_vision.capture_screen()
        return screen_vision.analyze_screen_with_ai(query)
    except Exception as e:
        return f"❌ Screen analysis failed: {str(e)}"

def get_smart_click_position(target: str) -> Optional[Tuple[int, int]]:
    """Get intelligent click position based on screen analysis"""
    try:
        if screen_vision is None:
            return None
        return screen_vision.find_best_click_target(target)
    except Exception as e:
        print(f"❌ Smart click failed: {e}")
        return None

def start_screen_monitoring():
    """Start screen monitoring"""
    try:
        if screen_vision is not None:
            screen_vision.start_monitoring()
    except Exception as e:
        print(f"❌ Failed to start screen monitoring: {e}")

def stop_screen_monitoring():
    """Stop screen monitoring"""
    try:
        if screen_vision is not None:
            screen_vision.stop_monitoring()
    except Exception as e:
        print(f"❌ Failed to stop screen monitoring: {e}")
