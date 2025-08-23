#!/usr/bin/env python3
"""
Test script for the Reinforcement Learning System
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rl_system():
    """Test the reinforcement learning system"""
    try:
        print("🧪 Testing Reinforcement Learning System...")
        
        # Import the RL system
        from Backend.ReinforcementLearningSystem import rl_system
        print("✅ RL System imported successfully")
        
        # Test basic functionality
        print("\n📊 Initial Learning Stats:")
        stats = rl_system.get_learning_stats()
        print(f"Total Feedback: {stats['total_feedback']}")
        print(f"Positive Feedback: {stats['positive_feedback']}")
        print(f"Negative Feedback: {stats['negative_feedback']}")
        
        # Test feedback processing
        print("\n🔄 Testing Feedback Processing...")
        
        # Test email feedback
        print("Testing email feedback: 'The email was too formal'")
        adjustments = rl_system.process_feedback("The email was too formal", "email draft", "email")
        print(f"Adjustments made: {adjustments}")
        
        # Test length feedback
        print("Testing length feedback: 'Make it shorter'")
        adjustments = rl_system.process_feedback("Make it shorter", "general response", "general")
        print(f"Adjustments made: {adjustments}")
        
        # Test tone feedback
        print("Testing tone feedback: 'Too friendly, make it professional'")
        adjustments = rl_system.process_feedback("Too friendly, make it professional", "chat response", "general")
        print(f"Adjustments made: {adjustments}")
        
        # Show updated stats
        print("\n📊 Updated Learning Stats:")
        stats = rl_system.get_learning_stats()
        print(f"Total Feedback: {stats['total_feedback']}")
        print(f"Positive Feedback: {stats['positive_feedback']}")
        print(f"Negative Feedback: {stats['negative_feedback']}")
        
        # Test style prompt generation
        print("\n🎨 Testing Style Prompt Generation...")
        style_prompt = rl_system.generate_style_prompt("draft an email", "work communication")
        print(f"Style guidance for email: {style_prompt}")
        
        style_prompt = rl_system.generate_style_prompt("write a report", "academic")
        print(f"Style guidance for report: {style_prompt}")
        
        # Test context-specific preferences
        print("\n🔍 Testing Context-Specific Preferences...")
        context_prefs = rl_system.style_preferences.get("context", {})
        print(f"Context preferences: {context_prefs}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing RL system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_feedback_handler():
    """Test the feedback handler"""
    try:
        print("\n🧪 Testing Feedback Handler...")
        
        from Backend.FeedbackHandler import handle_feedback_request, process_pending_feedback
        
        # Test feedback request handling
        print("Testing feedback request: 'The response was too long'")
        response = handle_feedback_request("The response was too long")
        print(f"Feedback handler response: {response}")
        
        # Test feedback processing
        print("Processing pending feedback...")
        result = process_pending_feedback()
        print(f"Feedback processing result: {result}")
        
        print("✅ Feedback Handler tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing feedback handler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Reinforcement Learning System Tests...\n")
    
    # Test RL system
    rl_success = test_rl_system()
    
    # Test feedback handler
    feedback_success = test_feedback_handler()
    
    print("\n" + "="*50)
    if rl_success and feedback_success:
        print("🎉 All tests passed! The RL system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    print("="*50)
