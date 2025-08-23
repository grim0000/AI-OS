import os
import json
from typing import Optional
from datetime import datetime

class FeedbackHandler:
    def __init__(self):
        self.feedback_file = "Frontend/Files/Feedback.data"
        self.feedback_history_file = "Data/feedback_history.json"
        
    def save_feedback(self, feedback: str, context: str = "", content_type: str = "general"):
        """Save feedback to temporary file for processing"""
        try:
            os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
            feedback_data = {
                "feedback": feedback,
                "context": context,
                "content_type": content_type,
                "timestamp": str(datetime.now())
            }
            
            with open(self.feedback_file, "w", encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def get_pending_feedback(self) -> Optional[dict]:
        """Get pending feedback from file"""
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, "r", encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading feedback: {e}")
        return None
    
    def clear_feedback(self):
        """Clear the feedback file after processing"""
        try:
            if os.path.exists(self.feedback_file):
                os.remove(self.feedback_file)
        except Exception as e:
            print(f"Error clearing feedback: {e}")
    
    def save_to_history(self, feedback_data: dict):
        """Save feedback to permanent history"""
        try:
            history = []
            if os.path.exists(self.feedback_history_file):
                with open(self.feedback_history_file, "r", encoding='utf-8') as f:
                    history = json.load(f)
            
            history.append(feedback_data)
            
            os.makedirs(os.path.dirname(self.feedback_history_file), exist_ok=True)
            with open(self.feedback_history_file, "w", encoding='utf-8') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"Error saving to history: {e}")

# Global instance
feedback_handler = FeedbackHandler()

def handle_feedback_request(query: str) -> str:
    """Handle feedback requests from users"""
    query_lower = query.lower()
    
    # Check if this is a feedback request
    if any(keyword in query_lower for keyword in ["feedback", "too long", "too short", "too formal", "too casual", "make it", "change", "adjust"]):
        # Extract the actual feedback
        feedback_text = query
        
        # Try to determine context and content type
        context = ""
        content_type = "general"
        
        # Look for context clues
        if "email" in query_lower or "mail" in query_lower:
            content_type = "email"
        elif "letter" in query_lower:
            content_type = "letter"
        elif "report" in query_lower or "document" in query_lower:
            content_type = "report"
        
        # Save feedback for processing
        if feedback_handler.save_feedback(feedback_text, context, content_type):
            return "Thank you for your feedback! I've recorded it and will use it to improve future responses."
        else:
            return "I encountered an error saving your feedback. Please try again."
    
    return None

def process_pending_feedback():
    """Process any pending feedback through the RL system"""
    try:
        from Backend.ReinforcementLearningSystem import rl_system
        
        feedback_data = feedback_handler.get_pending_feedback()
        if feedback_data:
            # Process through RL system
            adjustments = rl_system.process_feedback(
                feedback_data["feedback"],
                feedback_data["context"],
                feedback_data["content_type"]
            )
            
            # Save to history
            feedback_handler.save_to_history(feedback_data)
            
            # Clear the feedback file
            feedback_handler.clear_feedback()
            
            print(f"Processed feedback: {adjustments}")
            return True
            
    except ImportError:
        print("Warning: Reinforcement Learning System not available")
    except Exception as e:
        print(f"Error processing feedback: {e}")
    
    return False

if __name__ == "__main__":
    # Test feedback handling
    print(handle_feedback_request("The email was too formal, make it more casual"))
    process_pending_feedback()
