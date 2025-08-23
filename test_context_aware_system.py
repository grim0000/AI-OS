#!/usr/bin/env python3
"""
Test script for the Context-Aware Generation System
Demonstrates the hierarchical policy approach
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_context_extraction():
    """Test context extraction from various inputs"""
    print("🧪 Testing Context Extraction...\n")
    
    try:
        from Backend.ContextAwareRL import ContextAwareRLSystem
        
        rl_system = ContextAwareRLSystem()
        
        test_cases = [
            "I need to email my boss about the project deadline extension",
            "Send a casual message to my teammate about lunch",
            "Write a formal apology to a client for the delay",
            "Draft a quick update for the team chat",
            "Urgent request to the CEO about budget approval",
            "Hey there! Just checking in about the meeting tomorrow",
            "To whom it may concern, I am writing regarding..."
        ]
        
        for test_input in test_cases:
            context = rl_system.infer_context(test_input)
            print(f"📝 Input: {test_input}")
            print(f"🔍 Context: {context.recipient_role.value} via {context.channel.value}")
            print(f"   Stakes: {context.stakes.value}, Purpose: {context.purpose.value}")
            print(f"   Length: {context.length_budget}, Urgency: {context.urgency}")
            print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing context extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_policy_matching():
    """Test policy rule matching"""
    print("\n🧪 Testing Policy Rule Matching...\n")
    
    try:
        from Backend.ContextAwareRL import ContextAwareRLSystem, ContextFrame, RecipientRole, Channel, Stakes, Purpose
        
        rl_system = ContextAwareRLSystem()
        
        # Test boss email context
        boss_context = ContextFrame(
            recipient_role=RecipientRole.BOSS,
            channel=Channel.EMAIL,
            stakes=Stakes.HIGH,
            purpose=Purpose.REQUEST,
            org_style="default",
            length_budget="short",
            topic="work",
            urgency="normal"
        )
        
        matching_rules = rl_system.match_rules(boss_context)
        constraints = rl_system.compile_constraints(matching_rules)
        
        print(f"📋 Boss Email Context:")
        print(f"   Recipient: {boss_context.recipient_role.value}")
        print(f"   Channel: {boss_context.channel.value}")
        print(f"   Stakes: {boss_context.stakes.value}")
        print(f"   Purpose: {boss_context.purpose.value}")
        
        print(f"\n📏 Matching Rules ({len(matching_rules)}):")
        for rule in matching_rules:
            print(f"   - {rule.name}")
        
        print(f"\n🔒 Compiled Constraints:")
        for key, value in constraints.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing policy matching: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_content_validation():
    """Test content validation system"""
    print("\n🧪 Testing Content Validation...\n")
    
    try:
        from Backend.ContentValidator import ContentValidator
        
        validator = ContentValidator()
        
        # Test formal email content
        formal_email = """Dear Mr. Johnson,

I hope this email finds you well. I am writing to request an extension on the project deadline.

The current timeline has been impacted by unforeseen technical challenges that require additional development time.

Could you please consider extending the deadline by one week? This would allow us to deliver a higher quality product.

Thank you for your understanding.

Best regards,
John Smith"""
        
        constraints = {
            "tone": "formal",
            "length_budget": 120,
            "structure": ["salutation", "body", "clear_ask", "signoff"],
            "forbid": ["contractions", "emoji", "excessive_exclamation"]
        }
        
        context = {"recipient_role": "boss", "channel": "email"}
        
        result = validator.validate_content(formal_email, constraints, context)
        
        print(f"📧 Testing Formal Email Validation:")
        print(f"   Valid: {result.is_valid}")
        print(f"   Score: {result.score:.2f}")
        print(f"   Issues: {len(result.issues)}")
        print(f"   Suggestions: {len(result.suggestions)}")
        
        if result.issues:
            print(f"\n⚠️  Issues found:")
            for issue in result.issues:
                print(f"   - {issue}")
        
        if result.suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in result.suggestions:
                print(f"   - {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing content validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_generation():
    """Test the complete end-to-end generation flow"""
    print("\n🧪 Testing End-to-End Generation...\n")
    
    try:
        from Backend.ContextAwareGenerator import context_aware_generator
        
        test_inputs = [
            "I need to email my boss about the project deadline extension",
            "Send a casual message to my teammate about lunch",
            "Write a formal apology to a client for the delay"
        ]
        
        for test_input in test_inputs:
            print(f"🎯 Generating content for: {test_input}")
            result = context_aware_generator.generate_content(test_input)
            
            print(f"✅ Generated content ({len(result['content'])} chars)")
            print(f"📊 Validation score: {result['validation']['score']:.2f}")
            print(f"🔍 Context: {result['context']['recipient_role']} via {result['context']['channel']}")
            print(f"📏 Constraints applied: {len(result['constraints'])}")
            print(f"🧠 Memories used: {result['memories_used']}")
            
            if result['validation']['issues']:
                print(f"⚠️  Validation issues: {result['validation']['issues']}")
            
            print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing end-to-end generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_feedback_processing():
    """Test feedback processing and learning"""
    print("\n🧪 Testing Feedback Processing...\n")
    
    try:
        from Backend.ContextAwareGenerator import context_aware_generator
        from Backend.ContextAwareRL import ContextFrame, RecipientRole, Channel, Stakes, Purpose
        
        # Create a test context
        test_context = ContextFrame(
            recipient_role=RecipientRole.TEAMMATE,
            channel=Channel.SLACK,
            stakes=Stakes.LOW,
            purpose=Purpose.INFORM,
            org_style="default",
            length_budget="short",
            topic="casual",
            urgency="low"
        )
        
        # Process some feedback
        feedback_cases = [
            "The message was too formal for Slack",
            "Make it shorter next time",
            "Perfect! Just the right tone"
        ]
        
        for feedback in feedback_cases:
            print(f"📝 Processing feedback: {feedback}")
            result = context_aware_generator.process_feedback(feedback, test_context)
            print(f"   Labels: {result['labels']}")
            print(f"   Suggestions: {result['suggestions']}")
        
        # Show learning stats
        stats = context_aware_generator.get_learning_stats()
        print(f"\n📈 Learning Statistics:")
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Total policies: {stats['total_policies']}")
        print(f"   Contexts covered: {stats['contexts_covered']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing feedback processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_policy_management():
    """Test adding and managing policy rules"""
    print("\n🧪 Testing Policy Management...\n")
    
    try:
        from Backend.ContextAwareGenerator import context_aware_generator
        
        # Add a custom policy rule
        custom_policy = {
            "name": "urgent_request_policy",
            "when": {
                "urgency": "urgent",
                "stakes": "high"
            },
            "constraints": {
                "tone": "professional",
                "length_budget": 80,
                "structure": ["urgent_marker", "clear_ask", "deadline", "contact_info"],
                "forbid": ["casual_greetings", "unnecessary_details"]
            }
        }
        
        print(f"📋 Adding custom policy: {custom_policy['name']}")
        context_aware_generator.add_policy_rule(
            custom_policy["name"],
            custom_policy["when"],
            custom_policy["constraints"]
        )
        
        # Test the new policy
        test_input = "URGENT: Need immediate approval for budget increase"
        result = context_aware_generator.generate_content(test_input)
        
        print(f"✅ Tested new policy with: {test_input}")
        print(f"   Context: {result['context']['urgency']} urgency, {result['context']['stakes']} stakes")
        print(f"   Constraints: {len(result['constraints'])} rules applied")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing policy management: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Context-Aware Generation System Tests...\n")
    
    tests = [
        ("Context Extraction", test_context_extraction),
        ("Policy Matching", test_policy_matching),
        ("Content Validation", test_content_validation),
        ("End-to-End Generation", test_end_to_end_generation),
        ("Feedback Processing", test_feedback_processing),
        ("Policy Management", test_policy_management)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🔍 Running {test_name} Test...")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} test completed successfully!\n")
            else:
                print(f"❌ {test_name} test failed!\n")
        except Exception as e:
            print(f"💥 {test_name} test crashed: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The context-aware system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
