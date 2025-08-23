import json
import os
import pickle
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np

class ReinforcementLearningSystem:
    def __init__(self, data_file="Data/rl_data.json", model_file="Data/rl_model.pkl"):
        self.data_file = data_file
        self.model_file = model_file
        self.feedback_data = self.load_feedback_data()
        self.style_preferences = self.load_style_preferences()
        self.context_memory = {}
        
    def load_feedback_data(self) -> Dict[str, Any]:
        """Load existing feedback data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading feedback data: {e}")
        return {
            "feedback_history": [],
            "style_preferences": {},
            "context_patterns": {},
            "learning_stats": {
                "total_feedback": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "last_updated": str(datetime.now())
            }
        }
    
    def load_style_preferences(self) -> Dict[str, Dict[str, float]]:
        """Load learned style preferences"""
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Error loading style preferences: {e}")
        return {
            "email_style": {"formal": 0.5, "casual": 0.5, "professional": 0.5},
            "tone": {"friendly": 0.5, "professional": 0.5, "casual": 0.5},
            "length": {"concise": 0.5, "detailed": 0.5},
            "context": {}
        }
    
    def save_data(self):
        """Save feedback data and style preferences"""
        try:
            # Save feedback data
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
            
            # Save style preferences
            with open(self.model_file, 'wb') as f:
                pickle.dump(self.style_preferences, f)
                
        except Exception as e:
            print(f"Error saving RL data: {e}")
    
    def process_feedback(self, feedback: str, context: str = "", content_type: str = "general"):
        """Process user feedback and update learning model"""
        feedback = feedback.lower().strip()
        
        # Record feedback
        feedback_entry = {
            "timestamp": str(datetime.now()),
            "feedback": feedback,
            "context": context,
            "content_type": content_type,
            "processed": False
        }
        
        self.feedback_data["feedback_history"].append(feedback_entry)
        self.feedback_data["learning_stats"]["total_feedback"] += 1
        
        # Analyze feedback sentiment and extract style preferences
        style_adjustments = self.analyze_feedback(feedback, content_type)
        
        # Update style preferences
        self.update_style_preferences(style_adjustments, content_type)
        
        # Update context patterns
        self.update_context_patterns(context, feedback, content_type)
        
        # Mark as processed
        feedback_entry["processed"] = True
        
        # Save updated data
        self.save_data()
        
        return style_adjustments
    
    def analyze_feedback(self, feedback: str, content_type: str) -> Dict[str, float]:
        """Analyze feedback and extract style adjustments"""
        adjustments = {}
        
        print(f"Analyzing feedback: '{feedback}' for content_type: '{content_type}'")
        
        # Enhanced email-specific feedback
        if "email" in feedback or content_type == "email":
            # Length feedback for emails - check for specific patterns first
            if any(phrase in feedback for phrase in ["too short", "short", "brief", "small", "tiny", "make it longer", "expand"]):
                adjustments["length"] = {"concise": -0.3, "detailed": 0.3}
                print("Applied: Email too short - increasing detailed preference")
            elif any(phrase in feedback for phrase in ["too long", "long", "lengthy", "verbose", "wordy", "make it shorter"]):
                adjustments["length"] = {"concise": 0.3, "detailed": -0.3}
                print("Applied: Email too long - increasing concise preference")
            
            # Formality feedback for emails
            if any(phrase in feedback for phrase in ["too formal", "formal", "stiff", "rigid", "make it casual"]):
                adjustments["email_style"] = {"formal": -0.3, "casual": 0.3, "professional": -0.1}
                print("Applied: Email too formal - increasing casual preference")
            elif any(phrase in feedback for phrase in ["too casual", "casual", "informal", "make it formal", "more professional"]):
                adjustments["email_style"] = {"formal": 0.3, "casual": -0.3, "professional": 0.2}
                print("Applied: Email too casual - increasing formal preference")
        
        # General length feedback - use more precise pattern matching
        feedback_lower = feedback.lower()
        
        # Check for "too short" patterns first (more specific)
        if any(phrase in feedback_lower for phrase in ["too short", "too brief", "make it longer", "more details", "expand"]):
            adjustments["length"] = {"concise": -0.3, "detailed": 0.3}
            print("Applied: Too short - increasing detailed preference")
        # Check for "too long" patterns (more specific)
        elif any(phrase in feedback_lower for phrase in ["too long", "too lengthy", "too verbose", "too wordy", "make it shorter"]):
            adjustments["length"] = {"concise": 0.3, "detailed": -0.3}
            print("Applied: Too long - increasing concise preference")
        # Check for general length words (less specific, only if no specific patterns found)
        elif "short" in feedback_lower and "long" not in feedback_lower:
            adjustments["length"] = {"concise": -0.3, "detailed": 0.3}
            print("Applied: Short - increasing detailed preference")
        elif "long" in feedback_lower and "short" not in feedback_lower:
            adjustments["length"] = {"concise": 0.3, "detailed": -0.3}
            print("Applied: Long - increasing concise preference")
        
        # Tone feedback
        if any(word in feedback for word in ["too friendly", "very friendly", "too warm", "too personal"]):
            adjustments["tone"] = {"friendly": -0.3, "professional": 0.3, "casual": 0.1}
            print("Applied: Too friendly - increasing professional preference")
        elif any(word in feedback for word in ["not friendly", "too cold", "too distant", "make it friendlier"]):
            adjustments["tone"] = {"friendly": 0.3, "professional": -0.2, "casual": 0.2}
            print("Applied: Not friendly enough - increasing friendly preference")
        elif any(word in feedback for word in ["too professional", "too business", "make it casual"]):
            adjustments["tone"] = {"friendly": 0.2, "professional": -0.3, "casual": 0.3}
            print("Applied: Too professional - increasing casual preference")
        
        # Formality feedback (general)
        if any(word in feedback for word in ["too formal", "formal", "stiff", "rigid", "make it casual"]):
            adjustments["tone"] = {"friendly": 0.2, "professional": -0.2, "casual": 0.3}
            print("Applied: Too formal - increasing casual tone")
        elif any(word in feedback for word in ["too casual", "casual", "informal", "make it formal"]):
            adjustments["tone"] = {"friendly": 0.1, "professional": 0.3, "casual": -0.3}
            print("Applied: Too casual - increasing professional tone")
        
        # General positive/negative feedback
        if any(word in feedback for word in ["good", "great", "perfect", "excellent", "like", "well done", "nice"]):
            self.feedback_data["learning_stats"]["positive_feedback"] += 1
            print("Recorded positive feedback")
        elif any(word in feedback for word in ["bad", "wrong", "terrible", "hate", "dislike", "awful", "horrible"]):
            self.feedback_data["learning_stats"]["negative_feedback"] += 1
            print("Recorded negative feedback")
        
        print(f"Final adjustments: {adjustments}")
        return adjustments
    
    def update_style_preferences(self, adjustments: Dict[str, float], content_type: str):
        """Update style preferences based on feedback"""
        for category, changes in adjustments.items():
            if category in self.style_preferences:
                for style, adjustment in changes.items():
                    if style in self.style_preferences[category]:
                        # Apply adjustment with bounds
                        new_value = self.style_preferences[category][style] + adjustment
                        self.style_preferences[category][style] = max(0.0, min(1.0, new_value))
        
        # Update context-specific preferences
        if content_type not in self.style_preferences["context"]:
            self.style_preferences["context"][content_type] = {}
        
        for category, changes in adjustments.items():
            if category not in self.style_preferences["context"][content_type]:
                self.style_preferences["context"][content_type][category] = self.style_preferences[category].copy()
            
            for style, adjustment in changes.items():
                if style in self.style_preferences["context"][content_type][category]:
                    new_value = self.style_preferences["context"][content_type][category][style] + adjustment
                    self.style_preferences["context"][content_type][category][category] = max(0.0, min(1.0, new_value))
    
    def update_context_patterns(self, context: str, feedback: str, content_type: str):
        """Update context patterns for better learning"""
        if context not in self.feedback_data["context_patterns"]:
            self.feedback_data["context_patterns"][context] = {
                "feedback_count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "style_preferences": {}
            }
        
        pattern = self.feedback_data["context_patterns"][context]
        pattern["feedback_count"] += 1
        
        if any(word in feedback for word in ["good", "great", "perfect", "excellent", "like"]):
            pattern["positive_count"] += 1
        elif any(word in feedback for word in ["bad", "wrong", "terrible", "hate", "dislike"]):
            pattern["negative_count"] += 1
    
    def generate_style_prompt(self, task: str, context: str = "") -> str:
        """Generate style guidance based on learned preferences"""
        style_guidance = []
        
        # Determine content type
        content_type = "general"
        if "email" in task.lower() or "mail" in task.lower():
            content_type = "email"
        elif "report" in task.lower():
            content_type = "report"
        elif "letter" in task.lower():
            content_type = "letter"
        
        # Get context-specific preferences
        if content_type in self.style_preferences["context"]:
            preferences = self.style_preferences["context"][content_type]
        else:
            preferences = self.style_preferences
        
        # Only apply strong style guidance if there's significant preference
        # Email style guidance
        if content_type == "email":
            casual_pref = preferences.get("email_style", {}).get("casual", 0.5)
            formal_pref = preferences.get("email_style", {}).get("formal", 0.5)
            
            if casual_pref > 0.7:  # Only if strongly preferred
                style_guidance.append("Use a casual, friendly tone.")
            elif formal_pref > 0.7:  # Only if strongly preferred
                style_guidance.append("Use a formal, professional tone.")
            else:
                style_guidance.append("Use a balanced professional tone.")
        
        # Length guidance - only apply if there's a clear preference
        length_prefs = preferences.get("length", {})
        concise_pref = length_prefs.get("concise", 0.5)
        detailed_pref = length_prefs.get("detailed", 0.5)
        
        if concise_pref > 0.7:
            style_guidance.append("Keep the content concise and to the point.")
        elif detailed_pref > 0.7:
            style_guidance.append("Provide detailed explanations.")
        
        # Tone guidance - only apply if there's a clear preference
        tone_prefs = preferences.get("tone", {})
        friendly_pref = tone_prefs.get("friendly", 0.5)
        professional_pref = tone_prefs.get("professional", 0.5)
        
        if friendly_pref > 0.7:
            style_guidance.append("Maintain a warm, friendly tone.")
        elif professional_pref > 0.7:
            style_guidance.append("Use a professional tone.")
        
        # Only return guidance if we have meaningful preferences
        if style_guidance:
            return " ".join(style_guidance)
        else:
            return ""  # Return empty string instead of default guidance
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        stats = self.feedback_data["learning_stats"].copy()
        stats["style_preferences"] = self.style_preferences
        stats["total_contexts"] = len(self.feedback_data["context_patterns"])
        return stats
    
    def reset_learning(self):
        """Reset all learned preferences"""
        self.style_preferences = {
            "email_style": {"formal": 0.5, "casual": 0.5, "professional": 0.5},
            "tone": {"friendly": 0.5, "professional": 0.5, "casual": 0.5},
            "length": {"concise": 0.5, "detailed": 0.5},
            "context": {}
        }
        self.feedback_data["feedback_history"] = []
        self.feedback_data["context_patterns"] = {}
        self.feedback_data["learning_stats"]["total_feedback"] = 0
        self.feedback_data["learning_stats"]["positive_feedback"] = 0
        self.feedback_data["learning_stats"]["negative_feedback"] = 0
        self.save_data()

# Global RL system instance
rl_system = ReinforcementLearningSystem()
