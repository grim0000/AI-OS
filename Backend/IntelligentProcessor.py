import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .CNNLogAnalyzer import CNNLogAnalyzer

class IntelligentProcessor:
    """
    Dynamic intelligent processor that understands user queries,
    analyzes sentiment, and executes appropriate actions
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        
        # Initialize CNN Log Analyzer for bias optimization
        try:
            self.cnn_analyzer = CNNLogAnalyzer()
            self.logger.info("CNN Log Analyzer initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize CNN Log Analyzer: {e}")
            self.cnn_analyzer = None
        
        # Action registry - maps intents to functions
        self.action_registry = {
            'email': self._handle_email_actions,
            'automation': self._handle_automation_actions,
            'excel': self._handle_excel_actions,
            'chat': self._handle_chat_actions,
            'system': self._handle_system_actions,
            'web': self._handle_web_actions,
            'file': self._handle_file_actions,
            'music': self._handle_music_actions,
            'search': self._handle_search_actions,
            'calendar': self._handle_calendar_actions
        }
        
        # Sentiment analysis keywords
        self.sentiment_keywords = {
            'positive': ['happy', 'good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like'],
            'negative': ['sad', 'bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'frustrated'],
            'urgent': ['urgent', 'asap', 'immediately', 'now', 'quick', 'fast', 'emergency'],
            'casual': ['maybe', 'later', 'when convenient', 'sometime', 'relaxed']
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point for processing user queries
        """
        try:
            # Step 1: Analyze the query
            analysis = self._analyze_query(user_input)
            
            # Step 2: Generate execution plan
            plan = self._generate_execution_plan(analysis)
            
            # Step 3: Execute the plan
            results = self._execute_plan(plan)
            
            # Step 4: Return comprehensive response
            return {
                'success': True,
                'original_query': user_input,
                'analysis': analysis,
                'execution_plan': plan,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'original_query': user_input,
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_query(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user query for intent, sentiment, and context
        """
        analysis = {
            'intent': self._detect_intent(user_input),
            'sentiment': self._analyze_sentiment(user_input),
            'urgency': self._detect_urgency(user_input),
            'entities': self._extract_entities(user_input),
            'confidence': self._calculate_confidence(user_input)
        }
        
        self.logger.info(f"Query analysis: {analysis}")
        return analysis
    
    def _detect_intent(self, user_input: str) -> str:
        """
        Detect the primary intent of the user query
        """
        user_input_lower = user_input.lower()
        
        # Email-related intents
        if any(word in user_input_lower for word in ['email', 'mail', 'send', 'compose', 'draft']):
            return 'email'
        
        # Automation intents
        if any(word in user_input_lower for word in ['automate', 'script', 'task', 'workflow']):
            return 'automation'
        
        # Excel intents
        if any(word in user_input_lower for word in ['excel', 'spreadsheet', 'data', 'table', 'chart']):
            return 'excel'
        
        # Web intents
        if any(word in user_input_lower for word in ['search', 'google', 'browse', 'website', 'url']):
            return 'web'
        
        # File intents
        if any(word in user_input_lower for word in ['file', 'folder', 'document', 'open', 'save']):
            return 'file'
        
        # Music intents
        if any(word in user_input_lower for word in ['music', 'song', 'play', 'spotify', 'audio']):
            return 'music'
        
        # Calendar intents
        if any(word in user_input_lower for word in ['calendar', 'schedule', 'meeting', 'appointment', 'reminder']):
            return 'calendar'
        
        # System intents
        if any(word in user_input_lower for word in ['system', 'computer', 'settings', 'control']):
            return 'system'
        
        # Default to chat
        return 'chat'
    
    def _analyze_sentiment(self, user_input: str) -> Dict[str, float]:
        """
        Analyze sentiment of the user query
        """
        user_input_lower = user_input.lower()
        
        positive_score = sum(1 for word in self.sentiment_keywords['positive'] if word in user_input_lower)
        negative_score = sum(1 for word in self.sentiment_keywords['negative'] if word in user_input_lower)
        
        total_words = len(user_input.split())
        positive_ratio = positive_score / max(total_words, 1)
        negative_ratio = negative_score / max(total_words, 1)
        
        return {
            'positive': positive_ratio,
            'negative': negative_ratio,
            'neutral': 1 - (positive_ratio + negative_ratio),
            'overall': positive_ratio - negative_ratio
        }
    
    def _detect_urgency(self, user_input: str) -> str:
        """
        Detect urgency level of the query
        """
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in self.sentiment_keywords['urgent']):
            return 'high'
        elif any(word in user_input_lower for word in self.sentiment_keywords['casual']):
            return 'low'
        else:
            return 'medium'
    
    def _extract_entities(self, user_input: str) -> Dict[str, Any]:
        """
        Extract relevant entities from the query
        """
        entities = {
            'email_addresses': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input),
            'urls': re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', user_input),
            'file_paths': re.findall(r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*', user_input),
            'numbers': re.findall(r'\d+', user_input),
            'dates': re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', user_input)
        }
        
        return entities
    
    def _calculate_confidence(self, user_input: str) -> float:
        """
        Calculate confidence score for the analysis
        """
        # Simple confidence calculation based on query length and clarity
        words = user_input.split()
        confidence = min(len(words) / 10.0, 1.0)  # More words = higher confidence up to 1.0
        
        # Boost confidence for specific keywords
        specific_keywords = ['email', 'send', 'open', 'search', 'play', 'automate']
        if any(keyword in user_input.lower() for keyword in specific_keywords):
            confidence = min(confidence + 0.2, 1.0)
        
        return confidence
    
    def _generate_execution_plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a step-by-step execution plan based on analysis
        """
        intent = analysis['intent']
        sentiment = analysis['sentiment']
        urgency = analysis['urgency']
        
        plan = []
        
        # Add sentiment-based adjustments
        if sentiment['overall'] < -0.3:
            plan.append({
                'step': 'sentiment_handling',
                'action': 'acknowledge_negative_sentiment',
                'priority': 'high',
                'description': 'Acknowledge user frustration and provide reassurance'
            })
        
        # Add urgency-based adjustments
        if urgency == 'high':
            plan.append({
                'step': 'urgency_handling',
                'action': 'prioritize_execution',
                'priority': 'critical',
                'description': 'Prioritize this request for immediate execution'
            })
        
        # Add main action based on intent
        if intent in self.action_registry:
            plan.append({
                'step': 'main_action',
                'action': intent,
                'priority': 'high' if urgency == 'high' else 'medium',
                'description': f'Execute {intent} related actions',
                'handler': self.action_registry[intent]
            })
        
        # Add follow-up actions
        plan.append({
            'step': 'follow_up',
            'action': 'provide_feedback',
            'priority': 'low',
            'description': 'Provide execution feedback and next steps'
        })
        
        return plan
    
    def _execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute the generated plan step by step
        """
        results = {
            'steps_executed': [],
            'success_count': 0,
            'error_count': 0,
            'total_steps': len(plan)
        }
        
        for i, step in enumerate(plan):
            try:
                step_result = self._execute_step(step)
                results['steps_executed'].append({
                    'step_number': i + 1,
                    'step': step,
                    'result': step_result,
                    'status': 'success'
                })
                results['success_count'] += 1
                
            except Exception as e:
                self.logger.error(f"Error executing step {i + 1}: {str(e)}")
                results['steps_executed'].append({
                    'step_number': i + 1,
                    'step': step,
                    'result': {'error': str(e)},
                    'status': 'error'
                })
                results['error_count'] += 1
        
        return results
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step in the plan
        """
        action = step['action']
        
        if action == 'acknowledge_negative_sentiment':
            return {'message': 'I understand this might be frustrating. Let me help you resolve this quickly.'}
        
        elif action == 'prioritize_execution':
            return {'message': 'I\'ll handle this as a priority.'}
        
        elif action == 'provide_feedback':
            return {'message': 'Action completed. Is there anything else you need?'}
        
        elif action in self.action_registry:
            handler = step['handler']
            return handler(step)
        
        else:
            return {'message': f'Unknown action: {action}'}
    
    # Action handlers
    def _handle_email_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email-related actions"""
        return {
            'action': 'email',
            'message': 'Email action executed',
            'details': 'Email functionality will be implemented here'
        }
    
    def _handle_automation_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle automation-related actions"""
        return {
            'action': 'automation',
            'message': 'Automation action executed',
            'details': 'Automation functionality will be implemented here'
        }
    
    def _handle_excel_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Excel-related actions"""
        return {
            'action': 'excel',
            'message': 'Excel action executed',
            'details': 'Excel functionality will be implemented here'
        }
    
    def _handle_chat_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat-related actions"""
        return {
            'action': 'chat',
            'message': 'Chat response generated',
            'details': 'Chat functionality will be implemented here'
        }
    
    def _handle_system_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system-related actions"""
        return {
            'action': 'system',
            'message': 'System action executed',
            'details': 'System functionality will be implemented here'
        }
    
    def _handle_web_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web-related actions"""
        return {
            'action': 'web',
            'message': 'Web action executed',
            'details': 'Web functionality will be implemented here'
        }
    
    def _handle_file_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file-related actions"""
        return {
            'action': 'file',
            'message': 'File action executed',
            'details': 'File functionality will be implemented here'
        }
    
    def _handle_music_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle music-related actions"""
        return {
            'action': 'music',
            'message': 'Music action executed',
            'details': 'Music functionality will be implemented here'
        }
    
    def _handle_search_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search-related actions"""
        return {
            'action': 'search',
            'message': 'Search action executed',
            'details': 'Search functionality will be implemented here'
        }
    
    def _handle_calendar_actions(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar-related actions"""
        return {
            'action': 'calendar',
            'message': 'Calendar action executed',
            'details': 'Calendar functionality will be implemented here'
        }
