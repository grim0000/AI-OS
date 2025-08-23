import json
import os
import pickle
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

class Channel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WHATSAPP = "whatsapp"
    MEMO = "memo"
    GENERAL = "general"

class RecipientRole(Enum):
    BOSS = "boss"
    EXECUTIVE = "executive"
    TEAMMATE = "teammate"
    CLIENT = "client"
    RECRUITER = "recruiter"
    UNKNOWN = "unknown"

class Stakes(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Purpose(Enum):
    INFORM = "inform"
    REQUEST = "request"
    APOLOGIZE = "apologize"
    ESCALATE = "escalate"
    NEGOTIATE = "negotiate"
    STATUS = "status"
    GENERAL = "general"

@dataclass
class ContextFrame:
    """Context information extracted from user input"""
    recipient_role: RecipientRole
    channel: Channel
    stakes: Stakes
    purpose: Purpose
    org_style: str
    length_budget: str  # "short", "medium", "long"
    topic: str
    urgency: str  # "urgent", "normal", "low"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recipient_role": self.recipient_role.value,
            "channel": self.channel.value,
            "stakes": self.stakes.value,
            "purpose": self.purpose.value,
            "org_style": self.org_style,
            "length_budget": self.length_budget,
            "topic": self.topic,
            "urgency": self.urgency
        }

class PolicyRule:
    """A policy rule that defines constraints for specific contexts"""
    
    def __init__(self, name: str, when: Dict[str, Any], constraints: Dict[str, Any]):
        self.name = name
        self.when = when  # Context conditions
        self.constraints = constraints  # What to set/forbid
        
    def matches(self, context: ContextFrame) -> bool:
        """Check if this rule applies to the given context"""
        context_dict = context.to_dict()
        
        for key, values in self.when.items():
            if key not in context_dict:
                return False
            
            if isinstance(values, list):
                if context_dict[key] not in values:
                    return False
            else:
                if context_dict[key] != values:
                    return False
        
        return True
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get the constraints this rule enforces"""
        return self.constraints.copy()

class ContextAwareRLSystem:
    """
    Hierarchical policy system with context-aware learning
    Follows: Hard Constraints → Contextual Policies → Learned Preferences
    """
    
    def __init__(self, data_dir="Data"):
        self.data_dir = data_dir
        self.policies_file = os.path.join(data_dir, "policy_rules.json")
        self.memories_file = os.path.join(data_dir, "contextual_memories.json")
        self.preferences_file = os.path.join(data_dir, "learned_preferences.json")
        
        # Load components
        self.policy_rules = self.load_policy_rules()
        self.contextual_memories = self.load_contextual_memories()
        self.learned_preferences = self.load_learned_preferences()
        
        # Initialize default policies
        self.initialize_default_policies()
        
    def load_policy_rules(self) -> List[PolicyRule]:
        """Load policy rules from file"""
        try:
            if os.path.exists(self.policies_file):
                with open(self.policies_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    return [PolicyRule(**rule) for rule in rules_data]
        except Exception as e:
            print(f"Error loading policy rules: {e}")
        return []
    
    def load_contextual_memories(self) -> List[Dict[str, Any]]:
        """Load contextual memories from file"""
        try:
            if os.path.exists(self.memories_file):
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading contextual memories: {e}")
        return []
    
    def load_learned_preferences(self) -> Dict[str, Any]:
        """Load learned preferences from file"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading learned preferences: {e}")
        return {
            "style_preferences": {},
            "context_patterns": {},
            "feedback_history": []
        }
    
    def save_data(self):
        """Save all data to files"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Save policy rules
            rules_data = [
                {
                    "name": rule.name,
                    "when": rule.when,
                    "constraints": rule.constraints
                }
                for rule in self.policy_rules
            ]
            with open(self.policies_file, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
            
            # Save contextual memories
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(self.contextual_memories, f, indent=2, ensure_ascii=False)
            
            # Save learned preferences
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_preferences, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def initialize_default_policies(self):
        """Initialize default policy rules for common scenarios"""
        if not self.policy_rules:
            default_policies = [
                # Boss/Executive Email Policy (High Stakes)
                PolicyRule(
                    name="boss_email_defaults",
                    when={
                        "channel": "email",
                        "recipient_role": ["boss", "executive"],
                        "stakes": "high"
                    },
                    constraints={
                        "tone": "formal",
                        "length_budget": 120,
                        "structure": ["subject", "salutation", "summary", "body", "clear_ask", "signoff"],
                        "forbid": ["slang", "emoji", "excessive_exclamation", "contractions"],
                        "honorifics": True,
                        "hedging": "low"
                    }
                ),
                
                # Client Communication Policy
                PolicyRule(
                    name="client_communication",
                    when={
                        "recipient_role": "client",
                        "stakes": ["high", "medium"]
                    },
                    constraints={
                        "tone": "professional",
                        "length_budget": 200,
                        "structure": ["greeting", "context", "main_content", "next_steps", "closing"],
                        "forbid": ["slang", "emoji", "casual_greetings"],
                        "honorifics": True,
                        "hedging": "medium"
                    }
                ),
                
                # High-Stakes Request Policy
                PolicyRule(
                    name="high_stakes_request",
                    when={
                        "purpose": "request",
                        "stakes": "high"
                    },
                    constraints={
                        "structure": ["clear_ask", "deadline", "fallback_option", "rationale"],
                        "tone": "professional",
                        "length_budget": 150,
                        "forbid": ["vague_language", "missing_deadlines"]
                    }
                ),
                
                # Casual Team Communication
                PolicyRule(
                    name="casual_team_comm",
                    when={
                        "recipient_role": "teammate",
                        "stakes": "low",
                        "channel": ["slack", "teams"]
                    },
                    constraints={
                        "tone": "casual",
                        "length_budget": 100,
                        "allow": ["emoji", "contractions", "casual_greetings"],
                        "structure": ["greeting", "content", "closing"]
                    }
                )
            ]
            
            self.policy_rules = default_policies
            self.save_data()
    
    def infer_context(self, user_input: str, headers: Dict[str, str] = None) -> ContextFrame:
        """
        Extract context from user input and headers
        This is the lightweight classifier/extractor
        """
        user_input_lower = user_input.lower()
        
        # Extract recipient role
        recipient_role = RecipientRole.UNKNOWN
        if any(word in user_input_lower for word in ["boss", "manager", "supervisor", "executive", "ceo", "director"]):
            recipient_role = RecipientRole.BOSS
        elif any(word in user_input_lower for word in ["client", "customer", "vendor"]):
            recipient_role = RecipientRole.CLIENT
        elif any(word in user_input_lower for word in ["teammate", "colleague", "coworker", "peer"]):
            recipient_role = RecipientRole.TEAMMATE
        elif any(word in user_input_lower for word in ["recruiter", "hiring manager"]):
            recipient_role = RecipientRole.RECRUITER
        
        # Extract channel
        channel = Channel.GENERAL
        if any(word in user_input_lower for word in ["email", "mail", "e-mail"]):
            channel = Channel.EMAIL
        elif any(word in user_input_lower for word in ["slack", "message"]):
            channel = Channel.SLACK
        elif any(word in user_input_lower for word in ["teams", "microsoft teams"]):
            channel = Channel.TEAMS
        elif any(word in user_input_lower for word in ["whatsapp", "text", "sms"]):
            channel = Channel.WHATSAPP
        elif any(word in user_input_lower for word in ["memo", "document", "report"]):
            channel = Channel.MEMO
        
        # Determine stakes based on context
        stakes = Stakes.LOW
        if recipient_role in [RecipientRole.BOSS, RecipientRole.EXECUTIVE, RecipientRole.CLIENT]:
            stakes = Stakes.HIGH
        elif any(word in user_input_lower for word in ["urgent", "important", "critical", "deadline"]):
            stakes = Stakes.HIGH
        elif any(word in user_input_lower for word in ["request", "proposal", "negotiation"]):
            stakes = Stakes.MEDIUM
        
        # Extract purpose
        purpose = Purpose.GENERAL
        if any(word in user_input_lower for word in ["request", "ask", "need", "want"]):
            purpose = Purpose.REQUEST
        elif any(word in user_input_lower for word in ["inform", "update", "status", "report"]):
            purpose = Purpose.INFORM
        elif any(word in user_input_lower for word in ["apologize", "sorry", "apology"]):
            purpose = Purpose.APOLOGIZE
        elif any(word in user_input_lower for word in ["escalate", "urgent", "critical"]):
            purpose = Purpose.ESCALATE
        
        # Determine length budget
        length_budget = "medium"
        if any(word in user_input_lower for word in ["short", "brief", "concise"]):
            length_budget = "short"
        elif any(word in user_input_lower for word in ["detailed", "comprehensive", "long"]):
            length_budget = "long"
        
        # Extract topic (simplified)
        topic = "general"
        if any(word in user_input_lower for word in ["project", "work", "task"]):
            topic = "work"
        elif any(word in user_input_lower for word in ["meeting", "schedule", "appointment"]):
            topic = "scheduling"
        elif any(word in user_input_lower for word in ["problem", "issue", "bug"]):
            topic = "problem_solving"
        
        # Determine urgency
        urgency = "normal"
        if any(word in user_input_lower for word in ["urgent", "asap", "immediately", "now"]):
            urgency = "urgent"
        elif any(word in user_input_lower for word in ["whenever", "no rush", "take your time"]):
            urgency = "low"
        
        return ContextFrame(
            recipient_role=recipient_role,
            channel=channel,
            stakes=stakes,
            purpose=purpose,
            org_style="default",
            length_budget=length_budget,
            topic=topic,
            urgency=urgency
        )
    
    def match_rules(self, context: ContextFrame) -> List[PolicyRule]:
        """Find all policy rules that match the given context"""
        matching_rules = []
        for rule in self.policy_rules:
            if rule.matches(context):
                matching_rules.append(rule)
        return matching_rules
    
    def compile_constraints(self, rules: List[PolicyRule]) -> Dict[str, Any]:
        """Compile constraints from matching rules"""
        constraints = {}
        
        for rule in rules:
            rule_constraints = rule.get_constraints()
            for key, value in rule_constraints.items():
                if key not in constraints:
                    constraints[key] = value
                elif isinstance(value, list) and isinstance(constraints[key], list):
                    # Merge lists
                    constraints[key] = list(set(constraints[key] + value))
                elif isinstance(value, dict) and isinstance(constraints[key], dict):
                    # Merge dicts
                    constraints[key].update(value)
        
        return constraints
    
    def retrieve_memories(self, context: ContextFrame, must_match: List[str] = None, allow: List[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve memories that are compatible with the current context
        Gate retrieval by context to avoid conflicts
        """
        if must_match is None:
            must_match = ["channel", "recipient_role"]
        if allow is None:
            allow = ["purpose", "topic"]
        
        compatible_memories = []
        context_dict = context.to_dict()
        
        for memory in self.contextual_memories:
            memory_context = memory.get("context", {})
            
            # Check must-match constraints
            compatible = True
            for field in must_match:
                if field in context_dict and field in memory_context:
                    if context_dict[field] != memory_context[field]:
                        compatible = False
                        break
            
            if compatible:
                compatible_memories.append(memory)
        
        return compatible_memories
    
    def discard_conflicts(self, memories: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Remove memories that conflict with current constraints"""
        compatible_memories = []
        
        for memory in memories:
            memory_feedback = memory.get("signal", {}).get("labels", [])
            
            # Check for conflicts with constraints
            conflict = False
            for constraint_key, constraint_value in constraints.items():
                if constraint_key == "forbid":
                    for forbidden in constraint_value:
                        if forbidden in memory_feedback:
                            conflict = True
                            break
                elif constraint_key == "tone" and "tone" in memory:
                    if memory["tone"] != constraint_value:
                        conflict = True
                        break
            
            if not conflict:
                compatible_memories.append(memory)
        
        return compatible_memories
    
    def generate_system_prompt(self, context: ContextFrame, constraints: Dict[str, Any], memories: List[Dict[str, Any]]) -> str:
        """
        Generate a system prompt that combines hard constraints with contextual policies
        and learned preferences (only if non-conflicting)
        """
        prompt_parts = []
        
        # 1. Hard constraints (non-negotiable)
        if constraints:
            prompt_parts.append("Follow these constraints strictly:")
            
            if "tone" in constraints:
                prompt_parts.append(f"- Tone: {constraints['tone']}")
            
            if "length_budget" in constraints:
                prompt_parts.append(f"- Length: max {constraints['length_budget']} words")
            
            if "structure" in constraints:
                prompt_parts.append(f"- Structure: {', '.join(constraints['structure'])}")
            
            if "forbid" in constraints:
                forbidden = ", ".join(constraints["forbid"])
                prompt_parts.append(f"- Avoid: {forbidden}")
            
            if "honorifics" in constraints:
                prompt_parts.append("- Use appropriate titles and formal address")
        
        # 2. Context-specific guidance
        if context.recipient_role == RecipientRole.BOSS:
            prompt_parts.append("This is a high-stakes communication to your boss. Maintain professional tone and be concise.")
        elif context.recipient_role == RecipientRole.CLIENT:
            prompt_parts.append("This is client communication. Be professional, clear, and solution-oriented.")
        elif context.stakes == Stakes.HIGH:
            prompt_parts.append("This is a high-stakes communication. Be precise, professional, and thorough.")
        
        # 3. Learned preferences (only if non-conflicting)
        if memories:
            # Extract non-conflicting preferences
            preferences = self.extract_safe_preferences(memories, constraints)
            if preferences:
                prompt_parts.append("User preferences (apply if appropriate):")
                prompt_parts.extend([f"- {pref}" for pref in preferences])
        
        if not prompt_parts:
            return "Generate appropriate content for the given context."
        
        return "\n".join(prompt_parts)
    
    def extract_safe_preferences(self, memories: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[str]:
        """Extract user preferences that don't conflict with current constraints"""
        preferences = []
        
        for memory in memories:
            feedback = memory.get("signal", {}).get("labels", [])
            
            # Only include preferences that don't conflict with constraints
            safe = True
            for constraint_key, constraint_value in constraints.items():
                if constraint_key == "forbid":
                    for forbidden in constraint_value:
                        if forbidden in feedback:
                            safe = False
                            break
            
            if safe and feedback:
                # Convert feedback to preference guidance
                for label in feedback:
                    if label == "too_long" and "length_budget" not in constraints:
                        preferences.append("Keep content concise")
                    elif label == "too_short" and "length_budget" not in constraints:
                        preferences.append("Provide sufficient detail")
                    elif label == "too_formal" and "tone" not in constraints:
                        preferences.append("Use casual tone when appropriate")
                    elif label == "too_casual" and "tone" not in constraints:
                        preferences.append("Maintain professional tone")
        
        return list(set(preferences))  # Remove duplicates
    
    def process_feedback(self, feedback: str, context: ContextFrame, content: str = "") -> Dict[str, Any]:
        """
        Process user feedback and store it with full context
        This enables better learning while maintaining safety
        """
        feedback_lower = feedback.lower()
        
        # Extract feedback signals
        labels = []
        if any(word in feedback_lower for word in ["too long", "long", "lengthy", "verbose"]):
            labels.append("too_long")
        if any(word in feedback_lower for word in ["too short", "short", "brief", "insufficient"]):
            labels.append("too_short")
        if any(word in feedback_lower for word in ["too formal", "formal", "stiff", "rigid"]):
            labels.append("too_formal")
        if any(word in feedback_lower for word in ["too casual", "casual", "informal", "unprofessional"]):
            labels.append("too_casual")
        if any(word in feedback_lower for word in ["good", "great", "perfect", "excellent"]):
            labels.append("positive")
        if any(word in feedback_lower for word in ["bad", "wrong", "terrible", "hate"]):
            labels.append("negative")
        
        # Create memory entry
        memory = {
            "id": f"mem_{len(self.contextual_memories) + 1}",
            "timestamp": str(datetime.now()),
            "context": context.to_dict(),
            "content": content,
            "signal": {
                "labels": labels,
                "feedback_text": feedback
            },
            "suggested_fix": self.generate_suggestions(labels, context)
        }
        
        # Store memory
        self.contextual_memories.append(memory)
        
        # Update learned preferences (only for safe contexts)
        if context.stakes == Stakes.LOW:
            self.update_learned_preferences(labels, context)
        
        self.save_data()
        return {"labels": labels, "suggestions": memory["suggested_fix"]}
    
    def generate_suggestions(self, labels: List[str], context: ContextFrame) -> List[str]:
        """Generate suggestions for improvement based on feedback"""
        suggestions = []
        
        for label in labels:
            if label == "too_long":
                suggestions.append("make_shorter")
                suggestions.append("frontload_summary")
            elif label == "too_short":
                suggestions.append("add_details")
                suggestions.append("expand_explanation")
            elif label == "too_formal":
                if context.stakes == Stakes.LOW:
                    suggestions.append("use_casual_tone")
                else:
                    suggestions.append("maintain_professional_but_friendly")
            elif label == "too_casual":
                suggestions.append("use_professional_tone")
                suggestions.append("add_formal_greeting")
        
        return suggestions
    
    def update_learned_preferences(self, labels: List[str], context: ContextFrame):
        """Update learned preferences (only for low-stakes contexts)"""
        context_key = f"{context.channel.value}_{context.recipient_role.value}"
        
        if context_key not in self.learned_preferences["style_preferences"]:
            self.learned_preferences["style_preferences"][context_key] = {
                "tone": {"formal": 0.5, "casual": 0.5},
                "length": {"concise": 0.5, "detailed": 0.5}
            }
        
        prefs = self.learned_preferences["style_preferences"][context_key]
        
        # Update preferences based on feedback
        for label in labels:
            if label == "too_long":
                prefs["length"]["concise"] = min(1.0, prefs["length"]["concise"] + 0.2)
                prefs["length"]["detailed"] = max(0.0, prefs["length"]["detailed"] - 0.2)
            elif label == "too_short":
                prefs["length"]["concise"] = max(0.0, prefs["length"]["concise"] - 0.2)
                prefs["length"]["detailed"] = min(1.0, prefs["length"]["detailed"] + 0.2)
            elif label == "too_formal":
                if context.stakes == Stakes.LOW:
                    prefs["tone"]["casual"] = min(1.0, prefs["tone"]["casual"] + 0.2)
                    prefs["tone"]["formal"] = max(0.0, prefs["tone"]["formal"] - 0.2)
            elif label == "too_casual":
                prefs["tone"]["formal"] = min(1.0, prefs["tone"]["formal"] + 0.2)
                prefs["tone"]["casual"] = max(0.0, prefs["tone"]["casual"] - 0.2)
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        stats = {
            "total_memories": len(self.contextual_memories),
            "total_policies": len(self.policy_rules),
            "contexts_covered": len(set(mem["context"]["recipient_role"] for mem in self.contextual_memories)),
            "feedback_distribution": {},
            "policy_usage": {}
        }
        
        # Analyze feedback distribution
        for memory in self.contextual_memories:
            for label in memory["signal"]["labels"]:
                stats["feedback_distribution"][label] = stats["feedback_distribution"].get(label, 0) + 1
        
        # Analyze policy usage
        for memory in self.contextual_memories:
            context_key = f"{memory['context']['channel']}_{memory['context']['recipient_role']}"
            stats["policy_usage"][context_key] = stats["policy_usage"].get(context_key, 0) + 1
        
        return stats

# Global instance
context_aware_rl = ContextAwareRLSystem()
