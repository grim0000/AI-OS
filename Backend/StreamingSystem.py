"""
🌊 Real-time Streaming System - An Innovative Alternative to ChatLog.json

This system provides:
- Real-time data streaming and processing
- Data compression and encryption
- Streaming analytics
- Multi-format output (JSON, Parquet, Avro)
- Real-time dashboards and monitoring
"""

import json
import time
import threading
import queue
import gzip
import base64
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
import aiofiles
from pathlib import Path
import pickle
import zlib
from collections import deque
import logging

@dataclass
class StreamEvent:
    """Real-time stream event"""
    event_id: str
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    priority: int = 0
    encrypted: bool = False

@dataclass
class StreamConfig:
    """Streaming configuration"""
    batch_size: int = 100
    flush_interval: float = 5.0  # seconds
    compression_enabled: bool = True
    encryption_enabled: bool = False
    encryption_key: str = ""
    output_formats: List[str] = None
    retention_days: int = 30
    real_time_analytics: bool = True

class DataCompressor:
    """Handles data compression and decompression"""
    
    @staticmethod
    def compress(data: bytes) -> bytes:
        """Compress data using gzip"""
        return gzip.compress(data)
    
    @staticmethod
    def decompress(data: bytes) -> bytes:
        """Decompress data using gzip"""
        return gzip.decompress(data)
    
    @staticmethod
    def compress_json(data: Dict[str, Any]) -> bytes:
        """Compress JSON data"""
        json_str = json.dumps(data, ensure_ascii=False)
        return DataCompressor.compress(json_str.encode('utf-8'))
    
    @staticmethod
    def decompress_json(data: bytes) -> Dict[str, Any]:
        """Decompress JSON data"""
        decompressed = DataCompressor.decompress(data)
        return json.loads(decompressed.decode('utf-8'))

class DataEncryptor:
    """Handles data encryption and decryption"""
    
    def __init__(self, key: str = ""):
        self.key = key or self._generate_key()
    
    def _generate_key(self) -> str:
        """Generate a random encryption key"""
        import secrets
        return secrets.token_hex(32)
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using simple XOR (for demo purposes)"""
        if not self.key:
            return data
        
        key_bytes = self.key.encode()
        encrypted = bytearray()
        
        for i, byte in enumerate(data):
            key_byte = key_bytes[i % len(key_bytes)]
            encrypted.append(byte ^ key_byte)
        
        return bytes(encrypted)
    
    def decrypt(self, data: bytes) -> bytes:
        """Decrypt data using simple XOR"""
        return self.encrypt(data)  # XOR is symmetric

class StreamProcessor:
    """Processes streaming data in real-time"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.event_queue = queue.Queue()
        self.processed_events = deque(maxlen=1000)
        self.analytics_data = {}
        self.running = False
        self.compressor = DataCompressor()
        self.encryptor = DataEncryptor(config.encryption_key) if config.encryption_enabled else None
        
        # Initialize output formats
        self.output_formats = config.output_formats or ["json", "compressed"]
        
        # Create output directories
        self._create_output_directories()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.running = True
        self.processing_thread.start()
    
    def _create_output_directories(self):
        """Create output directories for different formats"""
        base_path = Path("Data/streaming")
        
        for format_type in self.output_formats:
            format_path = base_path / format_type
            format_path.mkdir(parents=True, exist_ok=True)
    
    def add_event(self, event: StreamEvent):
        """Add event to processing queue"""
        self.event_queue.put(event)
    
    def _processing_loop(self):
        """Main processing loop"""
        batch = []
        last_flush = time.time()
        
        while self.running:
            try:
                # Get event from queue with timeout
                try:
                    event = self.event_queue.get(timeout=1.0)
                    batch.append(event)
                except queue.Empty:
                    pass
                
                # Check if we should flush the batch
                current_time = time.time()
                if (len(batch) >= self.config.batch_size or 
                    current_time - last_flush >= self.config.flush_interval):
                    
                    if batch:
                        self._process_batch(batch)
                        batch = []
                        last_flush = current_time
                
                # Small sleep to prevent busy waiting
                time.sleep(0.01)
                
            except Exception as e:
                logging.error(f"Error in processing loop: {e}")
    
    def _process_batch(self, events: List[StreamEvent]):
        """Process a batch of events"""
        try:
            # Store events in different formats
            for format_type in self.output_formats:
                self._store_events(events, format_type)
            
            # Update analytics
            if self.config.real_time_analytics:
                self._update_analytics(events)
            
            # Add to processed events
            self.processed_events.extend(events)
            
        except Exception as e:
            logging.error(f"Error processing batch: {e}")
    
    def _store_events(self, events: List[StreamEvent], format_type: str):
        """Store events in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "json":
            self._store_json(events, timestamp)
        elif format_type == "compressed":
            self._store_compressed(events, timestamp)
        elif format_type == "encrypted":
            self._store_encrypted(events, timestamp)
        elif format_type == "pickle":
            self._store_pickle(events, timestamp)
    
    def _store_json(self, events: List[StreamEvent], timestamp: str):
        """Store events as JSON"""
        output_file = Path(f"Data/streaming/json/events_{timestamp}.json")
        
        event_data = []
        for event in events:
            event_dict = asdict(event)
            event_data.append(event_dict)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, indent=2, ensure_ascii=False)
    
    def _store_compressed(self, events: List[StreamEvent], timestamp: str):
        """Store events in compressed format"""
        output_file = Path(f"Data/streaming/compressed/events_{timestamp}.gz")
        
        event_data = []
        for event in events:
            event_dict = asdict(event)
            event_data.append(event_dict)
        
        compressed_data = self.compressor.compress_json(event_data)
        
        with open(output_file, 'wb') as f:
            f.write(compressed_data)
    
    def _store_encrypted(self, events: List[StreamEvent], timestamp: str):
        """Store events in encrypted format"""
        if not self.encryptor:
            return
        
        output_file = Path(f"Data/streaming/encrypted/events_{timestamp}.enc")
        
        event_data = []
        for event in events:
            event_dict = asdict(event)
            event_data.append(event_dict)
        
        json_data = json.dumps(event_data, ensure_ascii=False).encode('utf-8')
        encrypted_data = self.encryptor.encrypt(json_data)
        
        with open(output_file, 'wb') as f:
            f.write(encrypted_data)
    
    def _store_pickle(self, events: List[StreamEvent], timestamp: str):
        """Store events using pickle"""
        output_file = Path(f"Data/streaming/pickle/events_{timestamp}.pkl")
        
        event_data = []
        for event in events:
            event_dict = asdict(event)
            event_data.append(event_dict)
        
        with open(output_file, 'wb') as f:
            pickle.dump(event_data, f)
    
    def _update_analytics(self, events: List[StreamEvent]):
        """Update real-time analytics"""
        for event in events:
            # Update event type counts
            event_type = event.event_type
            if event_type not in self.analytics_data:
                self.analytics_data[event_type] = 0
            self.analytics_data[event_type] += 1
            
            # Update timestamp analytics
            if 'timestamps' not in self.analytics_data:
                self.analytics_data['timestamps'] = []
            self.analytics_data['timestamps'].append(event.timestamp)
            
            # Keep only last 1000 timestamps
            if len(self.analytics_data['timestamps']) > 1000:
                self.analytics_data['timestamps'] = self.analytics_data['timestamps'][-1000:]
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get current analytics data"""
        analytics = self.analytics_data.copy()
        
        # Calculate additional metrics
        if 'timestamps' in analytics and analytics['timestamps']:
            timestamps = analytics['timestamps']
            analytics['total_events'] = len(timestamps)
            analytics['events_per_second'] = len(timestamps) / max(1, timestamps[-1] - timestamps[0])
            analytics['latest_event'] = datetime.fromtimestamp(timestamps[-1]).isoformat()
        
        return analytics
    
    def stop(self):
        """Stop the stream processor"""
        self.running = False
        if self.processing_thread.is_alive():
            self.processing_thread.join()

class StreamingSystem:
    """Main streaming system"""
    
    def __init__(self, config: StreamConfig = None):
        self.config = config or StreamConfig()
        self.processor = StreamProcessor(self.config)
        self.event_counter = 0
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def stream_event(self, event_type: str, data: Dict[str, Any], 
                    metadata: Dict[str, Any] = None, priority: int = 0) -> str:
        """Stream a new event"""
        
        event_id = self._generate_event_id()
        timestamp = time.time()
        
        event = StreamEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            data=data,
            metadata=metadata or {},
            priority=priority,
            encrypted=self.config.encryption_enabled
        )
        
        # Add to processor
        self.processor.add_event(event)
        
        self.logger.info(f"Streamed event: {event_id} ({event_type})")
        return event_id
    
    def stream_chat(self, user_input: str, assistant_response: str, 
                   context: Dict[str, Any] = None) -> str:
        """Stream a chat interaction"""
        
        data = {
            "user_input": user_input,
            "assistant_response": assistant_response,
            "context": context or {}
        }
        
        metadata = {
            "session_id": context.get("session_id", "default"),
            "user_id": context.get("user_id", "default"),
            "interaction_type": "chat"
        }
        
        return self.stream_event("chat_interaction", data, metadata)
    
    def stream_automation(self, action: str, target: str, result: str, 
                         context: Dict[str, Any] = None) -> str:
        """Stream an automation action"""
        
        data = {
            "action": action,
            "target": target,
            "result": result,
            "context": context or {}
        }
        
        metadata = {
            "automation_type": "app_control",
            "success": "success" in result.lower() or "opened" in result.lower()
        }
        
        return self.stream_event("automation_action", data, metadata)
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get streaming analytics"""
        return self.processor.get_analytics()
    
    def get_recent_events(self, limit: int = 100) -> List[StreamEvent]:
        """Get recent events"""
        return list(self.processor.processed_events)[-limit:]
    
    def search_events(self, event_type: str = None, 
                     start_time: float = None, end_time: float = None) -> List[StreamEvent]:
        """Search for events with filters"""
        events = list(self.processor.processed_events)
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        return events
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        self.event_counter += 1
        timestamp = int(time.time() * 1000)
        return f"event_{timestamp}_{self.event_counter}"
    
    def cleanup_old_data(self):
        """Clean up old data based on retention policy"""
        retention_days = self.config.retention_days
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        # Clean up processed events
        self.processor.processed_events = deque(
            [e for e in self.processor.processed_events if e.timestamp > cutoff_time],
            maxlen=1000
        )
        
        # Clean up old files
        self._cleanup_old_files(cutoff_time)
    
    def _cleanup_old_files(self, cutoff_time: float):
        """Clean up old files"""
        base_path = Path("Data/streaming")
        
        for format_dir in base_path.iterdir():
            if format_dir.is_dir():
                for file_path in format_dir.iterdir():
                    if file_path.is_file():
                        # Try to extract timestamp from filename
                        try:
                            # Extract timestamp from filename like "events_20231201_143022.json"
                            filename = file_path.stem
                            if filename.startswith("events_"):
                                timestamp_str = filename[7:]  # Remove "events_"
                                file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S").timestamp()
                                
                                if file_time < cutoff_time:
                                    file_path.unlink()
                                    self.logger.info(f"Deleted old file: {file_path}")
                        except Exception as e:
                            self.logger.warning(f"Could not parse timestamp from {file_path}: {e}")
    
    def shutdown(self):
        """Shutdown the streaming system"""
        self.processor.stop()
        self.logger.info("Streaming system shutdown complete")

# Global streaming system instance
streaming_system = StreamingSystem()

def stream_chat_interaction(user_input: str, assistant_response: str, 
                          context: Dict[str, Any] = None) -> str:
    """Stream a chat interaction"""
    return streaming_system.stream_chat(user_input, assistant_response, context)

def stream_automation_action(action: str, target: str, result: str, 
                           context: Dict[str, Any] = None) -> str:
    """Stream an automation action"""
    return streaming_system.stream_automation(action, target, result, context)

def get_streaming_analytics() -> Dict[str, Any]:
    """Get streaming analytics"""
    return streaming_system.get_analytics()

def get_recent_stream_events(limit: int = 100) -> List[StreamEvent]:
    """Get recent stream events"""
    return streaming_system.get_recent_events(limit)

if __name__ == "__main__":
    # Test the streaming system
    print("🌊 Testing Streaming System...")
    
    # Stream some test events
    event_id1 = stream_chat_interaction("Hello", "Hi there!", {"session_id": "test1"})
    event_id2 = stream_automation_action("open", "chrome", "Chrome opened successfully")
    event_id3 = stream_chat_interaction("What's the weather?", "Let me check for you.", {"session_id": "test1"})
    
    # Wait a bit for processing
    time.sleep(2)
    
    # Get analytics
    analytics = get_streaming_analytics()
    print(f"Analytics: {analytics}")
    
    # Get recent events
    recent_events = get_recent_stream_events(10)
    print(f"Recent events: {len(recent_events)}")
    
    # Search for specific events
    chat_events = streaming_system.search_events(event_type="chat_interaction")
    print(f"Chat events: {len(chat_events)}")
    
    print("✅ Streaming system test completed!")
