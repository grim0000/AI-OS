import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of content validation"""
    is_valid: bool
    issues: List[str]
    suggestions: List[str]
    score: float  # 0.0 to 1.0

class ContentValidator:
    """
    Post-generation content validator
    Checks content against policy constraints and provides suggestions
    """
    
    def __init__(self):
        # Common patterns for validation
        self.contractions = re.compile(r'\b\w+\'[a-z]+\b', re.IGNORECASE)
        self.excessive_exclamation = re.compile(r'!{2,}')
        self.emoji_pattern = re.compile(r'[^\w\s\.,!?;:()[\]{}"\'-]')
        self.slang_patterns = [
            r'\b(hey|hi|hello|yo)\b',
            r'\b(cool|awesome|great|nice)\b',
            r'\b(thanks|thx|tnx)\b',
            r'\b(bye|see ya|later)\b'
        ]
        
        # Professional language patterns
        self.professional_patterns = [
            r'\b(regarding|concerning|with respect to)\b',
            r'\b(please|kindly|would you)\b',
            r'\b(accordingly|therefore|thus)\b',
            r'\b(hereby|herein|hereto)\b'
        ]
    
    def validate_content(self, content: str, constraints: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """
        Validate content against policy constraints
        Returns validation result with issues and suggestions
        """
        issues = []
        suggestions = []
        score = 1.0
        
        # Check length constraints
        if "length_budget" in constraints:
            word_count = len(content.split())
            max_words = constraints["length_budget"]
            
            if word_count > max_words:
                issues.append(f"Content is {word_count} words, exceeds limit of {max_words}")
                suggestions.append(f"Reduce content by {word_count - max_words} words")
                score -= 0.3
            elif word_count < max_words * 0.5:
                issues.append(f"Content is {word_count} words, may be too brief")
                suggestions.append("Consider adding more detail")
                score -= 0.1
        
        # Check forbidden elements
        if "forbid" in constraints:
            for forbidden in constraints["forbid"]:
                if forbidden == "contractions":
                    contractions = self.contractions.findall(content)
                    if contractions:
                        issues.append(f"Found contractions: {', '.join(contractions)}")
                        suggestions.append("Replace contractions with full words")
                        score -= 0.2
                
                elif forbidden == "emoji":
                    emojis = self.emoji_pattern.findall(content)
                    if emojis:
                        issues.append(f"Found emoji-like characters: {', '.join(emojis)}")
                        suggestions.append("Remove emoji and special characters")
                        score -= 0.2
                
                elif forbidden == "excessive_exclamation":
                    exclamations = self.excessive_exclamation.findall(content)
                    if exclamations:
                        issues.append("Found excessive exclamation marks")
                        suggestions.append("Use single exclamation marks only")
                        score -= 0.1
                
                elif forbidden == "slang":
                    slang_found = []
                    for pattern in self.slang_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        slang_found.extend(matches)
                    
                    if slang_found:
                        issues.append(f"Found casual language: {', '.join(set(slang_found))}")
                        suggestions.append("Use more professional language")
                        score -= 0.2
        
        # Check structure requirements
        if "structure" in constraints:
            required_elements = constraints["structure"]
            missing_elements = []
            
            for element in required_elements:
                if element == "subject" and not self.has_subject(content):
                    missing_elements.append("subject line")
                elif element == "salutation" and not self.has_salutation(content):
                    missing_elements.append("proper greeting")
                elif element == "signoff" and not self.has_signoff(content):
                    missing_elements.append("proper closing")
                elif element == "clear_ask" and not self.has_clear_request(content):
                    missing_elements.append("clear request/ask")
            
            if missing_elements:
                issues.append(f"Missing required elements: {', '.join(missing_elements)}")
                suggestions.append(f"Add: {', '.join(missing_elements)}")
                score -= 0.3
        
        # Check tone appropriateness
        if "tone" in constraints:
            tone = constraints["tone"]
            if tone == "formal":
                if not self.is_formal_tone(content):
                    issues.append("Content is not sufficiently formal")
                    suggestions.append("Use more professional language and structure")
                    score -= 0.2
            elif tone == "casual":
                if not self.is_casual_tone(content):
                    issues.append("Content is too formal for casual context")
                    suggestions.append("Use more relaxed, friendly language")
                    score -= 0.2
        
        # Check honorifics requirement
        if constraints.get("honorifics", False):
            if not self.has_honorifics(content):
                issues.append("Missing appropriate titles and formal address")
                suggestions.append("Use proper titles (Mr., Ms., Dr., etc.)")
                score -= 0.2
        
        # Ensure score doesn't go below 0
        score = max(0.0, score)
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            score=score
        )
    
    def has_subject(self, content: str) -> bool:
        """Check if content has a subject line"""
        lines = content.split('\n')
        if len(lines) > 0:
            first_line = lines[0].strip()
            # Simple heuristic: subject line is usually short and doesn't end with punctuation
            return len(first_line) < 100 and not first_line.endswith(('.', '!', '?'))
        return False
    
    def has_salutation(self, content: str) -> bool:
        """Check if content has a proper greeting"""
        salutations = [
            r'^dear\s+\w+',
            r'^hello\s+\w+',
            r'^hi\s+\w+',
            r'^good\s+(morning|afternoon|evening)',
            r'^to\s+whom\s+it\s+may\s+concern'
        ]
        
        for pattern in salutations:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def has_signoff(self, content: str) -> bool:
        """Check if content has a proper closing"""
        signoffs = [
            r'sincerely',
            r'best\s+regards',
            r'thank\s+you',
            r'regards',
            r'yours\s+truly',
            r'respectfully'
        ]
        
        for pattern in signoffs:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def has_clear_request(self, content: str) -> bool:
        """Check if content has a clear request or ask"""
        request_patterns = [
            r'please\s+\w+',
            r'would\s+you\s+\w+',
            r'could\s+you\s+\w+',
            r'i\s+(need|want|request|ask)',
            r'request\s+that'
        ]
        
        for pattern in request_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def is_formal_tone(self, content: str) -> bool:
        """Check if content has a formal tone"""
        formal_indicators = 0
        casual_indicators = 0
        
        # Count formal language patterns
        for pattern in self.professional_patterns:
            formal_indicators += len(re.findall(pattern, content, re.IGNORECASE))
        
        # Count casual language patterns
        for pattern in self.slang_patterns:
            casual_indicators += len(re.findall(pattern, content, re.IGNORECASE))
        
        # Check for contractions
        contractions = len(self.contractions.findall(content))
        casual_indicators += contractions
        
        return formal_indicators > casual_indicators
    
    def is_casual_tone(self, content: str) -> bool:
        """Check if content has a casual tone"""
        return not self.is_formal_tone(content)
    
    def has_honorifics(self, content: str) -> bool:
        """Check if content uses proper titles"""
        honorifics = [
            r'\b(mr|mrs|ms|dr|prof|sir|madam)\.?\s+\w+',
            r'\b(mister|missus|miss|doctor|professor)\s+\w+'
        ]
        
        for pattern in honorifics:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def auto_revise(self, content: str, validation_result: ValidationResult) -> str:
        """
        Automatically revise content based on validation issues
        This is a simple revision system - in production you might use an LLM
        """
        revised_content = content
        
        for issue in validation_result.issues:
            if "contractions" in issue.lower():
                # Replace common contractions
                revised_content = re.sub(r'\bdon\'t\b', 'do not', revised_content, flags=re.IGNORECASE)
                revised_content = re.sub(r'\bcan\'t\b', 'cannot', revised_content, flags=re.IGNORECASE)
                revised_content = re.sub(r'\bwon\'t\b', 'will not', revised_content, flags=re.IGNORECASE)
                revised_content = re.sub(r'\bit\'s\b', 'it is', revised_content, flags=re.IGNORECASE)
                revised_content = re.sub(r'\bi\'m\b', 'I am', revised_content, flags=re.IGNORECASE)
            
            elif "excessive exclamation" in issue.lower():
                # Replace multiple exclamation marks with single ones
                revised_content = re.sub(r'!{2,}', '!', revised_content)
            
            elif "missing proper greeting" in issue.lower():
                # Add a generic greeting if none exists
                if not self.has_salutation(revised_content):
                    revised_content = "Dear Sir/Madam,\n\n" + revised_content
            
            elif "missing proper closing" in issue.lower():
                # Add a generic closing if none exists
                if not self.has_signoff(revised_content):
                    revised_content += "\n\nBest regards,\n[Your Name]"
        
        return revised_content

# Global validator instance
content_validator = ContentValidator()
