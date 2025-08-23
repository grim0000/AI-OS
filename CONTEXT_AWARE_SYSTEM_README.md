# Context-Aware Hierarchical Policy System for AI-OS-500pm

## 🎯 **Overview**

This system implements the **hierarchical policy approach** you described, ensuring that **hard constraints and contextual policies always override learned preferences**. This prevents the system from generating inappropriate responses in high-stakes situations like boss emails.

## 🏗️ **Architecture: Hard Constraints → Contextual Policies → Learned Preferences**

### **1. Hard Constraints (Non-Negotiable)**
- **Safety rules**: Company style guides, legal requirements, PII rules
- **Contextual policies**: Boss emails must be formal, respectful, concise
- **Channel requirements**: Email vs. Slack vs. Teams have different rules

### **2. Contextual Policy (Situation Aware)**
- **Recipient-based**: Boss/executive vs. teammate vs. client
- **Stakes assessment**: High/medium/low based on context
- **Purpose-driven**: Request, apology, status update, etc.
- **Channel-specific**: Email, Slack, Teams, WhatsApp, etc.

### **3. Learned Preferences (Soft, Context-Gated)**
- **Only applied when not conflicting** with hard constraints
- **Context-gated retrieval**: Won't fetch "be casual" memories for boss emails
- **Safe learning**: Only learns from low-stakes contexts

## 🔍 **How Context Inference Works**

The system automatically extracts context from user input:

```python
# Example: "I need to email my boss about the project deadline extension"
context = {
    "recipient_role": "boss",           # High stakes
    "channel": "email",                 # Formal medium
    "stakes": "high",                   # Automatic detection
    "purpose": "request",               # Deadline extension
    "length_budget": "short",           # Boss preference
    "urgency": "normal"                 # No urgent keywords
}
```

### **Context Detection Patterns**
- **Recipient**: "boss", "manager", "CEO", "client", "teammate"
- **Channel**: "email", "Slack", "Teams", "WhatsApp"
- **Stakes**: "urgent", "important", "critical", "deadline"
- **Purpose**: "request", "apologize", "inform", "escalate"

## 📋 **Default Policy Rules**

### **Boss/Executive Email Policy**
```json
{
  "name": "boss_email_defaults",
  "when": {
    "channel": "email",
    "recipient_role": ["boss", "executive"],
    "stakes": "high"
  },
  "constraints": {
    "tone": "formal",
    "length_budget": 120,
    "structure": ["subject", "salutation", "summary", "body", "clear_ask", "signoff"],
    "forbid": ["slang", "emoji", "excessive_exclamation", "contractions"],
    "honorifics": true,
    "hedging": "low"
  }
}
```

### **Client Communication Policy**
```json
{
  "name": "client_communication",
  "when": {
    "recipient_role": "client",
    "stakes": ["high", "medium"]
  },
  "constraints": {
    "tone": "professional",
    "length_budget": 200,
    "structure": ["greeting", "context", "main_content", "next_steps", "closing"],
    "forbid": ["slang", "emoji", "casual_greetings"],
    "honorifics": true
  }
}
```

### **Casual Team Communication**
```json
{
  "name": "casual_team_comm",
  "when": {
    "recipient_role": "teammate",
    "stakes": "low",
    "channel": ["slack", "teams"]
  },
  "constraints": {
    "tone": "casual",
    "length_budget": 100,
    "allow": ["emoji", "contractions", "casual_greetings"]
  }
}
```

## 🚀 **End-to-End Inference Flow**

### **Step 1: Extract Context**
```python
context = rl_system.infer_context(user_input, headers)
# Builds ContextFrame with recipient_role, channel, stakes, purpose, etc.
```

### **Step 2: Load Matching Rules**
```python
matching_rules = rl_system.match_rules(context)
constraints = rl_system.compile_constraints(matching_rules)
# Applies all rules that match the current context
```

### **Step 3: Gate Memory Retrieval**
```python
memories = rl_system.retrieve_memories(context, must_match=["channel", "recipient_role"])
memories = rl_system.discard_conflicts(memories, constraints)
# Only fetches memories compatible with current context
```

### **Step 4: Generate System Prompt**
```python
system_prompt = rl_system.generate_system_prompt(context, constraints, memories)
# Combines hard constraints + context guidance + safe preferences
```

### **Step 5: Generate & Validate**
```python
candidates = generate_candidates(user_input, system_prompt, n=3)
best_candidate = score_and_rank(candidates)
validation_result = validator.validate_content(best_candidate, constraints)
# Auto-revises if validation fails
```

## 🧠 **Memory Retrieval Gating**

The system **prevents conflicting memories** from entering the prompt:

```python
# Query: Only memories where channel=email AND recipient_role=boss
memories = retrieve_memories(context, must_match=["channel", "recipient_role"])

# If any memory conflicts with constraints, discard it
memories = discard_conflicts(memories, constraints)
```

**Example**: A "be casual" memory from Slack won't be used for boss emails because:
1. **Channel mismatch**: Slack ≠ Email
2. **Recipient mismatch**: Teammate ≠ Boss
3. **Constraint conflict**: Casual tone conflicts with formal requirement

## ✅ **Content Validation & Auto-Revision**

### **Post-Generation Checks**
- **Length validation**: Respects word count limits
- **Structure validation**: Ensures required elements present
- **Tone validation**: Checks formal/casual appropriateness
- **Content validation**: Removes forbidden elements

### **Auto-Revision Examples**
```python
# If contractions found in formal context
"Don't worry" → "Do not worry"

# If missing greeting
"Here's the update..." → "Dear Sir/Madam,\n\nHere's the update..."

# If missing signoff
"Thanks!" → "Thanks!\n\nBest regards,\n[Your Name]"
```

## 📊 **Learning & Feedback**

### **Safe Learning Contexts**
- **High-stakes feedback**: Stored but doesn't update preferences
- **Low-stakes feedback**: Updates learned preferences
- **Context-aware storage**: All feedback stored with full context

### **Feedback Processing**
```python
# High-stakes context (boss email)
if context.stakes == Stakes.HIGH:
    # Store feedback but don't update preferences
    store_memory(feedback, context)
else:
    # Safe to learn from this feedback
    update_learned_preferences(feedback, context)
```

## 🛠️ **Usage Examples**

### **Generate Boss Email**
```python
from Backend.ContextAwareGenerator import context_aware_generator

result = context_aware_generator.generate_content(
    "I need to email my boss about the project deadline extension"
)

print(f"Generated: {result['content']}")
print(f"Context: {result['context']['recipient_role']} via {result['context']['channel']}")
print(f"Validation Score: {result['validation']['score']:.2f}")
```

### **Add Custom Policy**
```python
# Add urgent request policy
context_aware_generator.add_policy_rule(
    "urgent_request_policy",
    {
        "urgency": "urgent",
        "stakes": "high"
    },
    {
        "tone": "professional",
        "length_budget": 80,
        "structure": ["urgent_marker", "clear_ask", "deadline"]
    }
)
```

### **Process Feedback**
```python
from Backend.ContextAwareRL import ContextFrame, RecipientRole, Channel, Stakes

context = ContextFrame(
    recipient_role=RecipientRole.TEAMMATE,
    channel=Channel.SLACK,
    stakes=Stakes.LOW,
    # ... other fields
)

result = context_aware_generator.process_feedback(
    "The message was too formal for Slack",
    context
)
```

## 🧪 **Testing the System**

Run the comprehensive test suite:

```bash
python test_context_aware_system.py
```

This tests:
- ✅ Context extraction
- ✅ Policy matching
- ✅ Content validation
- ✅ End-to-end generation
- ✅ Feedback processing
- ✅ Policy management

## 📁 **File Structure**

```
Backend/
├── ContextAwareRL.py          # Core RL system with policies
├── ContentValidator.py        # Post-generation validation
├── ContextAwareGenerator.py   # Main integration module
└── ReinforcementLearningSystem.py  # Original system (kept for compatibility)

test_context_aware_system.py   # Comprehensive test suite
```

## 🔒 **Safety Guarantees**

### **1. Policy Hierarchy Enforcement**
- Hard constraints **always override** learned preferences
- Contextual policies **always override** general preferences
- Learned preferences **only apply** when safe

### **2. Memory Gating**
- **No conflicting memories** can enter the prompt
- **Context-specific retrieval** prevents inappropriate suggestions
- **Constraint validation** ensures compliance

### **3. Content Validation**
- **Post-generation checks** catch policy violations
- **Auto-revision** fixes common issues
- **Validation scoring** provides quality metrics

## 🚀 **Integration with Existing System**

The new system can be used alongside the existing one:

```python
# Use new context-aware system for high-stakes content
if "boss" in user_input or "client" in user_input:
    result = context_aware_generator.generate_content(user_input)
else:
    # Use existing system for casual content
    result = rl_system.generate_style_prompt(user_input)
```

## 🎯 **Key Benefits**

1. **🔒 Safety First**: Hard constraints prevent inappropriate responses
2. **🎯 Context Aware**: Automatically detects situation and applies appropriate policies
3. **🧠 Smart Learning**: Learns preferences without compromising safety
4. **⚡ Fast Inference**: Lightweight context extraction and rule matching
5. **🔄 Auto-Revision**: Fixes validation issues automatically
6. **📊 Comprehensive Logging**: Full audit trail for learning and debugging

## 🔮 **Future Enhancements**

- **Advanced NLP**: Better context extraction using small transformers
- **Reward Models**: Trained models for candidate scoring
- **Multi-User**: Separate preference profiles per user
- **Web Interface**: Policy management dashboard
- **Export/Import**: Share policies across organizations

---

**This system ensures you'll never "lose your job" because an old "be casual" memory slips into a boss email!** 🎯✨
