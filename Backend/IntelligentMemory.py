"""
Intelligent Memory System - Replacement for ChatLog.json
Provides advanced memory capabilities including long-term memory, pattern learning, and context awareness.
"""

import sqlite3
import json
import datetime
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import threading

@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: Optional[int] = None
    timestamp: str = ""
    user_input: str = ""
    assistant_response: str = ""
    context: Dict[str, Any] = None
    intent: str = ""
    importance: float = 0.0
    automation_used: bool = False
    automation_action: str = ""

class IntelligentMemory:
    """Advanced memory system with learning and pattern recognition"""
    
    def __init__(self, db_path: str = "Data/intelligent_memory.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        self._load_existing_chatlog()
        
    def _init_database(self):
        """Initialize the SQLite database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main memories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    context TEXT,
                    intent TEXT,
                    importance REAL DEFAULT 0.0,
                    automation_used BOOLEAN DEFAULT FALSE,
                    automation_action TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_seen TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        print("🧠 Intelligent Memory System initialized!")
    
    def _load_existing_chatlog(self):
        """Migrate existing ChatLog.json data"""
        try:
            chatlog_path = Path("Data/ChatLog.json")
            if chatlog_path.exists():
                with open(chatlog_path, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                
                print(f"🔄 Migrating {len(old_data)} entries from ChatLog.json...")
                
                user_messages = []
                assistant_messages = []
                
                for entry in old_data:
                    if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                        if entry['role'] == 'user':
                            user_messages.append(entry['content'])
                        elif entry['role'] == 'assistant':
                            assistant_messages.append(entry['content'])
                
                for i in range(min(len(user_messages), len(assistant_messages))):
                    self.store_memory(
                        user_input=user_messages[i],
                        assistant_response=assistant_messages[i],
                        context={"source": "migration"}
                    )
                
                print("✅ Migration completed!")
                
        except Exception as e:
            print(f"⚠️ Migration failed: {e}")
    
    def store_memory(self, user_input: str, assistant_response: str, 
                    context: Dict[str, Any] = None, automation_action: str = "") -> int:
        """Store a new memory entry"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            intent = self._extract_intent(user_input)
            importance = self._calculate_importance(user_input, assistant_response)
            
            cursor.execute('''
                INSERT INTO memories 
                (timestamp, user_input, assistant_response, context, intent, importance, automation_used, automation_action)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.datetime.now().isoformat(),
                user_input,
                assistant_response,
                json.dumps(context or {}),
                intent,
                importance,
                bool(automation_action),
                automation_action
            ))
            
            memory_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return memory_id
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Retrieve memories relevant to the current query"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, timestamp, user_input, assistant_response, context, intent, importance, automation_used, automation_action
                FROM memories 
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            memories = []
            for row in cursor.fetchall():
                memory = MemoryEntry(
                    id=row[0],
                    timestamp=row[1],
                    user_input=row[2],
                    assistant_response=row[3],
                    context=json.loads(row[4]) if row[4] else {},
                    intent=row[5],
                    importance=row[6],
                    automation_used=bool(row[7]),
                    automation_action=row[8]
                )
                memories.append(memory)
            
            conn.close()
            return memories
    
    def get_contextual_response(self, query: str) -> str:
        """Generate a contextual response based on memory"""
        relevant_memories = self.get_relevant_memories(query, limit=3)
        
        if not relevant_memories:
            return ""
        
        context_parts = []
        for memory in relevant_memories:
            if memory.automation_used:
                context_parts.append(f"Previously, I helped you with {memory.automation_action}")
            else:
                context_parts.append(f"Earlier, you asked about '{memory.user_input}'")
        
        if context_parts:
            return " Based on our previous conversation: " + ". ".join(context_parts) + "."
        
        return ""
    
    def _extract_intent(self, text: str) -> str:
        """Extract intent from user input"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['open', 'start', 'launch']):
            return 'app_control'
        elif any(word in text_lower for word in ['search', 'find', 'look']):
            return 'search'
        elif any(word in text_lower for word in ['weather', 'temperature']):
            return 'weather'
        elif any(word in text_lower for word in ['excel', 'spreadsheet']):
            return 'excel'
        else:
            return 'general'
    
    def _calculate_importance(self, user_input: str, assistant_response: str) -> float:
        """Calculate importance score for a memory"""
        importance = 0.0
        
        # Length factor
        importance += min(len(user_input) / 100, 0.3)
        importance += min(len(assistant_response) / 200, 0.2)
        
        # Intent factor
        intent = self._extract_intent(user_input)
        if intent in ['app_control', 'excel']:
            importance += 0.3
        
        # Automation factor
        if 'open' in user_input.lower() or 'close' in user_input.lower():
            importance += 0.2
        
        return min(importance, 1.0)

# Global instance
intelligent_memory = IntelligentMemory()

# Convenience functions
def store_interaction(user_input: str, assistant_response: str, 
                     context: Dict[str, Any] = None, automation_action: str = "") -> int:
    """Store a new interaction in memory"""
    return intelligent_memory.store_memory(user_input, assistant_response, context, automation_action)

def get_contextual_response(query: str) -> str:
    """Get contextual response based on memory"""
    return intelligent_memory.get_contextual_response(query)

def record_automation_action(action_type: str, action_details: str, 
                           success: bool = True, user_feedback: str = "") -> int:
    """Record an automation action for learning"""
    # For now, store as a special type of interaction
    context = {
        "action_type": action_type,
        "action_details": action_details,
        "success": success,
        "user_feedback": user_feedback,
        "source": "automation"
    }
    
    return store_interaction(
        user_input=f"Automation: {action_type} - {action_details}",
        assistant_response=f"Action {'completed successfully' if success else 'failed'}. {user_feedback}",
        context=context,
        automation_action=action_type
    )
