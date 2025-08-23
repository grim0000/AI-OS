"""
Context-Aware Content Generator
Implements the hierarchical policy system with context-aware learning
"""

from typing import Dict, List, Any, Optional, Tuple
from .ContextAwareRL import ContextAwareRLSystem, ContextFrame
from .ContentValidator import ContentValidator, ValidationResult
import json
import os
from datetime import datetime

class ContextAwareGenerator:
    """
    Main content generation system that follows the hierarchical approach:
    Hard Constraints → Contextual Policies → Learned Preferences
    """
    
    def __init__(self):
        self.rl_system = ContextAwareRLSystem()
        self.validator = ContentValidator()
        
    def generate_content(self, user_input: str, headers: Dict[str, str] = None, n_candidates: int = 3) -> Dict[str, Any]:
        """
        Main content generation method following the inference flow:
        1. Extract context → build Context Frame
        2. Load rules → form hard constraints
        3. Gate retrieval → fetch only compatible memories
        4. Draft generation → produce N candidates obeying constraints
        5. Score candidates
        6. Pick best and validate
        7. Auto-revise if needed
        8. Log outcome for future RL
        """
        
        print(f"🎯 Generating content for: {user_input[:100]}...")
        
        # Step 1: Extract context
        context = self.rl_system.infer_context(user_input, headers)
        print(f"📋 Context: {context.recipient_role.value} via {context.channel.value}, {context.stakes.value} stakes")
        
        # Step 2: Load matching rules
        matching_rules = self.rl_system.match_rules(context)
        constraints = self.rl_system.compile_constraints(matching_rules)
        print(f"📏 Constraints: {len(constraints)} rules applied")
        
        # Step 3: Gate retrieval - fetch only compatible memories
        memories = self.rl_system.retrieve_memories(context)
        memories = self.rl_system.discard_conflicts(memories, constraints)
        print(f"🧠 Retrieved {len(memories)} compatible memories")
        
        # Step 4: Generate system prompt
        system_prompt = self.rl_system.generate_system_prompt(context, constraints, memories)
        print(f"📝 System prompt generated ({len(system_prompt)} chars)")
        
        # Step 5: Generate candidates (in a real system, this would call an LLM)
        candidates = self.generate_candidates(user_input, system_prompt, n_candidates)
        
        # Step 6: Score and rank candidates
        scored_candidates = self.score_candidates(candidates, context, constraints)
        best_candidate = max(scored_candidates, key=lambda x: x[1])[0]
        
        # Step 7: Validate and auto-revise if needed
        validation_result = self.validator.validate_content(best_candidate, constraints, context.to_dict())
        
        if not validation_result.is_valid:
            print(f"⚠️  Validation issues found: {validation_result.issues}")
            best_candidate = self.validator.auto_revise(best_candidate, validation_result)
            # Re-validate after revision
            validation_result = self.validator.validate_content(best_candidate, constraints, context.to_dict())
        
        # Step 8: Log outcome for future RL
        self.log_generation_outcome(context, best_candidate, validation_result, user_input)
        
        return {
            "content": best_candidate,
            "context": context.to_dict(),
            "constraints": constraints,
            "system_prompt": system_prompt,
            "validation": {
                "is_valid": validation_result.is_valid,
                "score": validation_result.score,
                "issues": validation_result.issues,
                "suggestions": validation_result.suggestions
            },
            "candidates_generated": n_candidates,
            "memories_used": len(memories)
        }
    
    def generate_candidates(self, user_input: str, system_prompt: str, n: int) -> List[str]:
        """
        Generate multiple content candidates
        In a real system, this would call an LLM with different parameters
        For now, we'll create template-based candidates
        """
        candidates = []
        
        # This is a simplified candidate generation
        # In production, you'd call your LLM with different prompts/parameters
        
        # Candidate 1: Direct approach
        candidates.append(f"Based on your request: {user_input}\n\n{system_prompt}")
        
        # Candidate 2: Structured approach
        candidates.append(f"Let me address your request step by step:\n\n{user_input}\n\n{system_prompt}")
        
        # Candidate 3: Contextual approach
        candidates.append(f"Considering the context and requirements:\n\n{user_input}\n\n{system_prompt}")
        
        return candidates[:n]
    
    def score_candidates(self, candidates: List[str], context: ContextFrame, constraints: Dict[str, Any]) -> List[Tuple[str, float]]:
        """
        Score candidates using a simple heuristic approach
        In production, you'd use a trained reward model
        """
        scored = []
        
        for candidate in candidates:
            score = 0.0
            
            # Length scoring
            word_count = len(candidate.split())
            if "length_budget" in constraints:
                max_words = constraints["length_budget"]
                if word_count <= max_words:
                    score += 0.3
                else:
                    score += max(0, 0.3 - (word_count - max_words) * 0.01)
            else:
                # Prefer medium length if no constraint
                if 50 <= word_count <= 200:
                    score += 0.3
            
            # Structure scoring
            if "structure" in constraints:
                required_elements = constraints["structure"]
                for element in required_elements:
                    if element in candidate.lower():
                        score += 0.1
            
            # Tone scoring
            if "tone" in constraints:
                tone = constraints["tone"]
                if tone == "formal" and self.validator.is_formal_tone(candidate):
                    score += 0.2
                elif tone == "casual" and self.validator.is_casual_tone(candidate):
                    score += 0.2
            
            # Content relevance scoring - use context topic instead of user_input
            if context.topic and context.topic != "general":
                if context.topic in candidate.lower():
                    score += 0.2
            
            scored.append((candidate, score))
        
        return scored
    
    def log_generation_outcome(self, context: ContextFrame, content: str, validation_result: ValidationResult, user_input: str):
        """Log the generation outcome for future reinforcement learning"""
        outcome = {
            "timestamp": str(datetime.now()),
            "context": context.to_dict(),
            "user_input": user_input,
            "generated_content": content,
            "validation_score": validation_result.score,
            "validation_issues": validation_result.issues,
            "success": validation_result.is_valid
        }
        
        # Store in RL system for learning
        # This could be expanded to include user feedback later
        print(f"📊 Logged generation outcome: score {validation_result.score:.2f}, valid: {validation_result.is_valid}")
    
    def process_feedback(self, feedback: str, context: ContextFrame, content: str = "") -> Dict[str, Any]:
        """Process user feedback through the context-aware RL system"""
        return self.rl_system.process_feedback(feedback, context, content)
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        return self.rl_system.get_learning_stats()
    
    def add_policy_rule(self, name: str, when: Dict[str, Any], constraints: Dict[str, Any]):
        """Add a new policy rule to the system"""
        from .ContextAwareRL import PolicyRule
        new_rule = PolicyRule(name, when, constraints)
        self.rl_system.policy_rules.append(new_rule)
        self.rl_system.save_data()
        print(f"✅ Added new policy rule: {name}")
    
    def test_context_extraction(self, test_inputs: List[str]) -> List[Dict[str, Any]]:
        """Test context extraction with various inputs"""
        results = []
        
        for test_input in test_inputs:
            context = self.rl_system.infer_context(test_input)
            results.append({
                "input": test_input,
                "context": context.to_dict()
            })
        
        return results
    
    def test_policy_matching(self, test_context: ContextFrame) -> Dict[str, Any]:
        """Test which policies match a given context"""
        matching_rules = self.rl_system.match_rules(test_context)
        constraints = self.rl_system.compile_constraints(matching_rules)
        
        return {
            "context": test_context.to_dict(),
            "matching_rules": [rule.name for rule in matching_rules],
            "compiled_constraints": constraints
        }

# Global instance
context_aware_generator = ContextAwareGenerator()

# Example usage functions
def generate_boss_email(user_input: str) -> Dict[str, Any]:
    """Generate a boss email using context-aware generation"""
    return context_aware_generator.generate_content(user_input)

def generate_client_communication(user_input: str) -> Dict[str, Any]:
    """Generate client communication using context-aware generation"""
    return context_aware_generator.generate_content(user_input)

def test_system():
    """Test the context-aware generation system"""
    test_inputs = [
        "I need to email my boss about the project deadline extension",
        "Send a casual message to my teammate about lunch",
        "Write a formal apology to a client for the delay",
        "Draft a quick update for the team chat"
    ]
    
    print("🧪 Testing Context-Aware Generation System...\n")
    
    for test_input in test_inputs:
        print(f"📝 Input: {test_input}")
        result = context_aware_generator.generate_content(test_input)
        print(f"✅ Generated content ({len(result['content'])} chars)")
        print(f"📊 Validation score: {result['validation']['score']:.2f}")
        print(f"🔍 Context: {result['context']['recipient_role']} via {result['context']['channel']}")
        print("-" * 50)
    
    print("\n📈 Learning Statistics:")
    stats = context_aware_generator.get_learning_stats()
    print(f"Total memories: {stats['total_memories']}")
    print(f"Total policies: {stats['total_policies']}")
    print(f"Contexts covered: {stats['contexts_covered']}")

if __name__ == "__main__":
    test_system()
