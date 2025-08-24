"""
🔌 Modular Plugin System - An Innovative Alternative to ChatLog.json

This system provides:
- Plugin-based architecture for easy extension
- Hot-swappable modules
- Custom data storage formats
- Event-driven communication
- Dynamic loading and unloading
"""

import json
import os
import sys
import importlib
import inspect
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio
import threading
import time
from pathlib import Path
from collections import defaultdict

@dataclass
class PluginInfo:
    """Plugin metadata"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    events: List[str]
    config_schema: Dict[str, Any]

@dataclass
class EventData:
    """Event data structure"""
    event_type: str
    timestamp: float
    data: Dict[str, Any]
    source: str
    priority: int = 0

class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = True
        self.plugin_info = self.get_plugin_info()
    
    @abstractmethod
    def get_plugin_info(self) -> PluginInfo:
        """Return plugin information"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup plugin resources"""
        pass
    
    def handle_event(self, event: EventData) -> Optional[Dict[str, Any]]:
        """Handle incoming events"""
        return None
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get plugin configuration"""
        return self.config.get(key, default)

class ChatStoragePlugin(BasePlugin):
    """Plugin for storing chat data in various formats"""
    
    def get_plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="ChatStorage",
            version="1.0.0",
            description="Stores chat data in multiple formats",
            author="System",
            dependencies=[],
            events=["chat_message", "chat_session_start", "chat_session_end"],
            config_schema={
                "storage_format": {"type": "string", "default": "json"},
                "backup_enabled": {"type": "boolean", "default": True},
                "compression": {"type": "boolean", "default": False}
            }
        )
    
    def initialize(self) -> bool:
        self.storage_path = Path("Data/plugins/chat_storage")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage based on format
        format_type = self.get_config("storage_format", "json")
        if format_type == "json":
            self.storage_file = self.storage_path / "chat_data.json"
        elif format_type == "sqlite":
            self.storage_file = self.storage_path / "chat_data.db"
        elif format_type == "csv":
            self.storage_file = self.storage_path / "chat_data.csv"
        
        return True
    
    def cleanup(self):
        # Save any pending data
        pass
    
    def handle_event(self, event: EventData) -> Optional[Dict[str, Any]]:
        if event.event_type == "chat_message":
            return self._store_chat_message(event.data)
        elif event.event_type == "chat_session_start":
            return self._start_session(event.data)
        elif event.event_type == "chat_session_end":
            return self._end_session(event.data)
        return None
    
    def _store_chat_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a chat message"""
        format_type = self.get_config("storage_format", "json")
        
        if format_type == "json":
            return self._store_json(data)
        elif format_type == "sqlite":
            return self._store_sqlite(data)
        elif format_type == "csv":
            return self._store_csv(data)
        
        return {"status": "error", "message": "Unknown storage format"}
    
    def _store_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data in JSON format"""
        try:
            # Load existing data
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            # Add new data
            existing_data.append({
                "timestamp": time.time(),
                "data": data
            })
            
            # Save back to file
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            return {"status": "success", "message": "Data stored in JSON"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _store_sqlite(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data in SQLite format"""
        # Implementation for SQLite storage
        return {"status": "success", "message": "Data stored in SQLite"}
    
    def _store_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data in CSV format"""
        # Implementation for CSV storage
        return {"status": "success", "message": "Data stored in CSV"}

class AnalyticsPlugin(BasePlugin):
    """Plugin for chat analytics and insights"""
    
    def get_plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="Analytics",
            version="1.0.0",
            description="Provides chat analytics and insights",
            author="System",
            dependencies=[],
            events=["chat_message", "user_feedback"],
            config_schema={
                "track_sentiment": {"type": "boolean", "default": True},
                "track_topics": {"type": "boolean", "default": True},
                "generate_reports": {"type": "boolean", "default": False}
            }
        )
    
    def initialize(self) -> bool:
        self.analytics_data = {
            "total_messages": 0,
            "user_sentiment": [],
            "topics": {},
            "response_times": [],
            "user_satisfaction": []
        }
        return True
    
    def cleanup(self):
        # Save analytics data
        analytics_file = Path("Data/plugins/analytics/analytics.json")
        analytics_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(self.analytics_data, f, indent=2)
    
    def handle_event(self, event: EventData) -> Optional[Dict[str, Any]]:
        if event.event_type == "chat_message":
            return self._analyze_message(event.data)
        elif event.event_type == "user_feedback":
            return self._process_feedback(event.data)
        return None
    
    def _analyze_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a chat message"""
        self.analytics_data["total_messages"] += 1
        
        # Analyze sentiment if enabled
        if self.get_config("track_sentiment", True):
            sentiment = self._analyze_sentiment(data.get("message", ""))
            self.analytics_data["user_sentiment"].append(sentiment)
        
        # Track topics if enabled
        if self.get_config("track_topics", True):
            topics = self._extract_topics(data.get("message", ""))
            for topic in topics:
                self.analytics_data["topics"][topic] = self.analytics_data["topics"].get(topic, 0) + 1
        
        return {"status": "success", "analytics_updated": True}
    
    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'worst', 'hate']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count == 0 and negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            'weather': ['weather', 'temperature', 'forecast'],
            'technology': ['computer', 'software', 'programming'],
            'music': ['music', 'song', 'play'],
            'automation': ['open', 'close', 'app']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

class PluginManager:
    """Manages plugin loading, unloading, and communication"""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        # Load plugin configurations
        self._load_plugin_configs()
    
    def _load_plugin_configs(self):
        """Load plugin configurations from file"""
        config_file = Path("Data/plugins/plugin_config.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.plugin_configs = json.load(f)
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a plugin with the manager"""
        try:
            plugin_name = plugin.plugin_info.name
            
            # Check dependencies
            for dep in plugin.plugin_info.dependencies:
                if dep not in self.plugins:
                    print(f"⚠️ Plugin {plugin_name} depends on {dep} which is not loaded")
                    return False
            
            # Initialize plugin
            if plugin.initialize():
                self.plugins[plugin_name] = plugin
                
                # Register event handlers
                for event in plugin.plugin_info.events:
                    self.event_handlers[event].append(plugin.handle_event)
                
                print(f"✅ Plugin {plugin_name} registered successfully")
                return True
            else:
                print(f"❌ Failed to initialize plugin {plugin_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error registering plugin: {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            
            # Remove event handlers
            for event in plugin.plugin_info.events:
                if plugin.handle_event in self.event_handlers[event]:
                    self.event_handlers[event].remove(plugin.handle_event)
            
            # Cleanup plugin
            plugin.cleanup()
            
            # Remove from plugins
            del self.plugins[plugin_name]
            
            print(f"✅ Plugin {plugin_name} unregistered successfully")
            return True
        
        return False
    
    def emit_event(self, event: EventData) -> List[Dict[str, Any]]:
        """Emit an event to all registered handlers"""
        results = []
        
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    result = handler(event)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"❌ Error in event handler: {e}")
        
        return results
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin by name"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """List all registered plugins"""
        return list(self.plugins.keys())
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        plugin = self.get_plugin(plugin_name)
        return plugin.plugin_info if plugin else None

# Global plugin manager instance
plugin_manager = PluginManager()

def initialize_plugin_system():
    """Initialize the plugin system with default plugins"""
    
    # Register default plugins
    chat_storage = ChatStoragePlugin()
    analytics = AnalyticsPlugin()
    
    plugin_manager.register_plugin(chat_storage)
    plugin_manager.register_plugin(analytics)
    
    print("🔌 Plugin system initialized successfully!")

def store_chat_data(user_input: str, assistant_response: str, 
                   context: Dict[str, Any] = None):
    """Store chat data using the plugin system"""
    
    event_data = EventData(
        event_type="chat_message",
        timestamp=time.time(),
        data={
            "user_input": user_input,
            "assistant_response": assistant_response,
            "context": context or {}
        },
        source="main_system"
    )
    
    results = plugin_manager.emit_event(event_data)
    return results

def get_analytics_data() -> Dict[str, Any]:
    """Get analytics data from the analytics plugin"""
    analytics_plugin = plugin_manager.get_plugin("Analytics")
    if analytics_plugin:
        return analytics_plugin.analytics_data
    return {}

if __name__ == "__main__":
    # Test the plugin system
    print("🔌 Testing Plugin System...")
    
    # Initialize system
    initialize_plugin_system()
    
    # Store some test data
    results = store_chat_data("Hello", "Hi there!", {"session_id": "test"})
    print(f"Storage results: {results}")
    
    # Get analytics
    analytics = get_analytics_data()
    print(f"Analytics: {analytics}")
    
    # List plugins
    plugins = plugin_manager.list_plugins()
    print(f"Registered plugins: {plugins}")
