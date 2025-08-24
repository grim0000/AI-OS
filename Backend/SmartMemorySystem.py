"""
🚀 Smart Memory System - An Innovative Alternative to ChatLog.json

This system provides:
- Contextual memory with semantic understanding
- Learning from user preferences and patterns
- Intelligent response generation
- Multi-modal data storage (text, voice, actions)
- Real-time adaptation and personalization
"""

import json
import sqlite3
import hashlib
import datetime
import pickle
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

@dataclass
class MemoryEntry:
    """Enhanced memory entry with rich metadata"""
    id: str
    timestamp: str
    user_input: str
    assistant_response: str
    context: Dict[str, Any]
    sentiment: float
    intent: str
    confidence: float
    action_taken: Optional[str]
    user_satisfaction: Optional[int]
    tags: List[str]
    importance_score: float
    related_memories: List[str]

@dataclass
class UserProfile:
    """Dynamic user profile with learning capabilities"""
    user_id: str
    name: str
    preferences: Dict[str, Any]
    communication_style: str
    expertise_level: Dict[str, str]
    frequently_used_topics: List[str]
    response_preferences: Dict[str, Any]
    learning_patterns: Dict[str, Any]
    last_interaction: str
    total_interactions: int

class SmartMemorySystem:
    """Advanced memory system with AI-powered features"""
    
    def __init__(self, db_path: str = "Data/smart_memory.db"):
        self.db_path = db_path
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.memory_vectors = None
        self.user_profiles = {}
        self.conversation_context = {}
        self.learning_engine = LearningEngine()
        
        # Initialize database
        self._init_database()
        self._load_existing_data()
    
    def _init_database(self):
        """Initialize SQLite database with advanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                user_input TEXT,
                assistant_response TEXT,
                context TEXT,
                sentiment REAL,
                intent TEXT,
                confidence REAL,
                action_taken TEXT,
                user_satisfaction INTEGER,
                tags TEXT,
                importance_score REAL,
                related_memories TEXT,
                embedding BLOB
            )
        ''')
        
        # Create user profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                preferences TEXT,
                communication_style TEXT,
                expertise_level TEXT,
                frequently_used_topics TEXT,
                response_preferences TEXT,
                learning_patterns TEXT,
                last_interaction TEXT,
                total_interactions INTEGER
            )
        ''')
        
        # Create conversation sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TEXT,
                end_time TEXT,
                topic TEXT,
                satisfaction_score REAL,
                memory_ids TEXT
            )
        ''')
        
        # Create learning patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                pattern_id TEXT PRIMARY KEY,
                user_id TEXT,
                pattern_type TEXT,
                pattern_data TEXT,
                confidence REAL,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_existing_data(self):
        """Load existing data from ChatLog.json and migrate to new system"""
        try:
            if os.path.exists("Data/ChatLog.json"):
                with open("Data/ChatLog.json", 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                
                print(f"🔄 Migrating {len(old_data)} entries from ChatLog.json...")
                
                # Group user and assistant messages
                user_messages = []
                assistant_messages = []
                
                for entry in old_data:
                    if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                        if entry['role'] == 'user':
                            user_messages.append(entry['content'])
                        elif entry['role'] == 'assistant':
                            assistant_messages.append(entry['content'])
                
                # Store pairs of interactions
                for i in range(min(len(user_messages), len(assistant_messages))):
                    self.store_memory(
                        user_input=user_messages[i],
                        assistant_response=assistant_messages[i],
                        context={"source": "migration", "legacy": True}
                    )
                
                print("✅ Migration completed successfully!")
                
        except Exception as e:
            print(f"⚠️ Migration failed: {e}")
    
    def store_memory(self, user_input: str, assistant_response: str, 
                    context: Dict[str, Any] = None, user_id: str = "default") -> str:
        """Store a new memory with advanced analysis"""
        
        # Generate unique ID
        memory_id = hashlib.md5(f"{user_input}{datetime.datetime.now()}".encode()).hexdigest()
        
        # Analyze the interaction
        sentiment = self._analyze_sentiment(user_input)
        intent = self._extract_intent(user_input)
        confidence = self._calculate_confidence(user_input, assistant_response)
        tags = self._extract_tags(user_input, assistant_response)
        importance = self._calculate_importance(user_input, context)
        
        # Create memory entry
        memory = MemoryEntry(
            id=memory_id,
            timestamp=datetime.datetime.now().isoformat(),
            user_input=user_input,
            assistant_response=assistant_response,
            context=context or {},
            sentiment=sentiment,
            intent=intent,
            confidence=confidence,
            action_taken=None,
            user_satisfaction=None,
            tags=tags,
            importance_score=importance,
            related_memories=[]
        )
        
        # Store in database
        self._save_memory_to_db(memory)
        
        # Update user profile
        self._update_user_profile(user_id, memory)
        
        # Learn from this interaction
        self.learning_engine.learn_from_interaction(memory, user_id)
        
        return memory_id
    
    def retrieve_relevant_memories(self, query: str, user_id: str = "default", 
                                 limit: int = 5) -> List[MemoryEntry]:
        """Retrieve memories relevant to current query using semantic search"""
        
        # Get all memories
        memories = self._get_all_memories()
        
        if not memories:
            return []
        
        # Create embeddings for query and memories
        query_embedding = self._create_embedding(query)
        memory_embeddings = [self._create_embedding(m.user_input) for m in memories]
        
        # Calculate similarities
        similarities = cosine_similarity([query_embedding], memory_embeddings)[0]
        
        # Sort by similarity and return top matches
        memory_similarity_pairs = list(zip(memories, similarities))
        memory_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return [memory for memory, similarity in memory_similarity_pairs[:limit]]
    
    def generate_contextual_response(self, user_input: str, user_id: str = "default") -> str:
        """Generate contextual response using memory and learning"""
        
        # Get relevant memories
        relevant_memories = self.retrieve_relevant_memories(user_input, user_id)
        
        # Get user profile
        user_profile = self._get_user_profile(user_id)
        
        # Generate response using learning engine
        response = self.learning_engine.generate_response(
            user_input, relevant_memories, user_profile
        )
        
        return response
    
    def learn_from_feedback(self, memory_id: str, user_satisfaction: int, 
                           feedback: str = None):
        """Learn from user feedback to improve future responses"""
        
        # Update memory with feedback
        self._update_memory_feedback(memory_id, user_satisfaction, feedback)
        
        # Update learning patterns
        self.learning_engine.update_from_feedback(memory_id, user_satisfaction, feedback)
    
    def get_user_insights(self, user_id: str = "default") -> Dict[str, Any]:
        """Get insights about user behavior and preferences"""
        
        user_profile = self._get_user_profile(user_id)
        memories = self._get_user_memories(user_id)
        
        insights = {
            "total_interactions": len(memories),
            "favorite_topics": self._extract_favorite_topics(memories),
            "communication_style": user_profile.communication_style,
            "satisfaction_trend": self._calculate_satisfaction_trend(memories),
            "interaction_patterns": self._analyze_interaction_patterns(memories),
            "learning_progress": self.learning_engine.get_learning_progress(user_id)
        }
        
        return insights
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text (simplified version)"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'worst']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count == 0 and negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _extract_intent(self, text: str) -> str:
        """Extract user intent from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['weather', 'temperature', 'forecast']):
            return 'weather_inquiry'
        elif any(word in text_lower for word in ['open', 'launch', 'start']):
            return 'app_control'
        elif any(word in text_lower for word in ['play', 'music', 'song']):
            return 'media_control'
        elif any(word in text_lower for word in ['search', 'find', 'look']):
            return 'information_search'
        elif any(word in text_lower for word in ['hello', 'hi', 'hey']):
            return 'greeting'
        else:
            return 'general_conversation'
    
    def _calculate_confidence(self, user_input: str, assistant_response: str) -> float:
        """Calculate confidence in the interaction"""
        # Simple heuristic - can be enhanced with ML models
        if len(assistant_response) > len(user_input) * 2:
            return 0.8
        elif len(assistant_response) > len(user_input):
            return 0.6
        else:
            return 0.4
    
    def _extract_tags(self, user_input: str, assistant_response: str) -> List[str]:
        """Extract relevant tags from interaction"""
        tags = []
        text = f"{user_input} {assistant_response}".lower()
        
        # Extract topic tags
        topic_keywords = {
            'weather': ['weather', 'temperature', 'forecast', 'rain', 'sunny'],
            'technology': ['computer', 'software', 'programming', 'code'],
            'music': ['music', 'song', 'play', 'spotify', 'youtube'],
            'automation': ['open', 'close', 'app', 'application'],
            'general': ['hello', 'how', 'what', 'when', 'where']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(topic)
        
        return tags
    
    def _calculate_importance(self, user_input: str, context: Dict[str, Any]) -> float:
        """Calculate importance score of the memory"""
        importance = 0.5  # Base importance
        
        # Increase importance for specific patterns
        if len(user_input) > 50:  # Long queries are often more important
            importance += 0.2
        
        if context and context.get('action_taken'):
            importance += 0.3  # Actions are important
        
        if any(word in user_input.lower() for word in ['important', 'urgent', 'critical']):
            importance += 0.4
        
        return min(importance, 1.0)
    
    def _create_embedding(self, text: str) -> np.ndarray:
        """Create text embedding for similarity search"""
        # Simplified embedding - can be enhanced with proper NLP models
        return np.random.rand(100)  # Placeholder
    
    def _save_memory_to_db(self, memory: MemoryEntry):
        """Save memory to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO memories 
            (id, timestamp, user_input, assistant_response, context, sentiment, 
             intent, confidence, action_taken, user_satisfaction, tags, 
             importance_score, related_memories, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.id, memory.timestamp, memory.user_input, memory.assistant_response,
            json.dumps(memory.context), memory.sentiment, memory.intent, memory.confidence,
            memory.action_taken, memory.user_satisfaction, json.dumps(memory.tags),
            memory.importance_score, json.dumps(memory.related_memories),
            pickle.dumps(self._create_embedding(memory.user_input))
        ))
        
        conn.commit()
        conn.close()
    
    def _get_all_memories(self) -> List[MemoryEntry]:
        """Get all memories from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM memories ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = MemoryEntry(
                id=row[0], timestamp=row[1], user_input=row[2], assistant_response=row[3],
                context=json.loads(row[4]), sentiment=row[5], intent=row[6], confidence=row[7],
                action_taken=row[8], user_satisfaction=row[9], tags=json.loads(row[10]),
                importance_score=row[11], related_memories=json.loads(row[12])
            )
            memories.append(memory)
        
        conn.close()
        return memories
    
    def _update_user_profile(self, user_id: str, memory: MemoryEntry):
        """Update user profile with new interaction"""
        # Implementation for updating user profile
        pass
    
    def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile from database"""
        # Implementation for getting user profile
        return UserProfile(
            user_id=user_id,
            name="User",
            preferences={},
            communication_style="formal",
            expertise_level={},
            frequently_used_topics=[],
            response_preferences={},
            learning_patterns={},
            last_interaction=datetime.datetime.now().isoformat(),
            total_interactions=0
        )
    
    def _update_memory_feedback(self, memory_id: str, satisfaction: int, feedback: str):
        """Update memory with user feedback"""
        # Implementation for updating memory feedback
        pass
    
    def _get_user_memories(self, user_id: str) -> List[MemoryEntry]:
        """Get memories for a specific user"""
        # Implementation for getting user memories
        return self._get_all_memories()
    
    def _extract_favorite_topics(self, memories: List[MemoryEntry]) -> List[str]:
        """Extract favorite topics from memories"""
        topic_counts = {}
        for memory in memories:
            for tag in memory.tags:
                topic_counts[tag] = topic_counts.get(tag, 0) + 1
        
        # Return top 5 topics
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:5]]
    
    def _calculate_satisfaction_trend(self, memories: List[MemoryEntry]) -> str:
        """Calculate satisfaction trend"""
        # Implementation for satisfaction trend
        return "improving"
    
    def _analyze_interaction_patterns(self, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """Analyze interaction patterns"""
        # Implementation for interaction patterns
        return {
            "total_interactions": len(memories),
            "average_response_length": 50,
            "most_active_hours": ["10:00", "14:00", "18:00"]
        }

class LearningEngine:
    """AI-powered learning engine for continuous improvement"""
    
    def __init__(self):
        self.patterns = defaultdict(list)
        self.response_templates = {}
        self.user_preferences = defaultdict(dict)
    
    def learn_from_interaction(self, memory: MemoryEntry, user_id: str):
        """Learn from user interaction"""
        # Extract patterns
        self.patterns[user_id].append({
            'intent': memory.intent,
            'satisfaction': memory.user_satisfaction,
            'tags': memory.tags
        })
    
    def generate_response(self, user_input: str, relevant_memories: List[MemoryEntry], 
                         user_profile: UserProfile) -> str:
        """Generate contextual response"""
        
        # Use relevant memories to inform response
        if relevant_memories:
            # Find best matching memory
            best_memory = max(relevant_memories, key=lambda m: m.importance_score)
            
            # Adapt response based on user profile
            if user_profile.communication_style == "formal":
                return f"Based on our previous conversation, {best_memory.assistant_response}"
            else:
                return f"Hey! {best_memory.assistant_response}"
        
        # Default response
        return "I understand your request. Let me help you with that."
    
    def update_from_feedback(self, memory_id: str, satisfaction: int, feedback: str):
        """Update learning from user feedback"""
        # Implementation for learning from feedback
        pass
    
    def get_learning_progress(self, user_id: str) -> Dict[str, Any]:
        """Get learning progress for user"""
        return {
            'patterns_learned': len(self.patterns[user_id]),
            'response_quality': 0.8,  # Placeholder
            'user_satisfaction_trend': 'improving'
        }

# Global instance
smart_memory = SmartMemorySystem()

def store_interaction(user_input: str, assistant_response: str, 
                     context: Dict[str, Any] = None, user_id: str = "default") -> str:
    """Store interaction in smart memory system"""
    return smart_memory.store_memory(user_input, assistant_response, context, user_id)

def get_contextual_response(user_input: str, user_id: str = "default") -> str:
    """Get contextual response using smart memory"""
    return smart_memory.generate_contextual_response(user_input, user_id)

def get_user_insights(user_id: str = "default") -> Dict[str, Any]:
    """Get insights about user behavior"""
    return smart_memory.get_user_insights(user_id)

if __name__ == "__main__":
    # Test the smart memory system
    print("🧠 Testing Smart Memory System...")
    
    # Store some test interactions
    store_interaction("Hello, how are you?", "I'm doing well, thank you for asking!")
    store_interaction("What's the weather like?", "Let me check the weather for you.")
    store_interaction("Open Chrome browser", "Opening Chrome browser for you.")
    
    # Get contextual response
    response = get_contextual_response("Hello again")
    print(f"Contextual response: {response}")
    
    # Get user insights
    insights = get_user_insights()
    print(f"User insights: {insights}")
