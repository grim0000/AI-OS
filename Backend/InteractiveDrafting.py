import json
import os
from groq import Groq
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get('GroqAPIKey')
client = Groq(api_key=GroqAPIKey)

class InteractiveDrafting:
    def __init__(self):
        self.current_session = None
        self.session_file = "Frontend/Files/DraftingSession.data"
        self.questions_file = "Frontend/Files/DraftingQuestions.data"
        
    def start_drafting_session(self, content_type, initial_prompt):
        """Start a new drafting session"""
        session = {
            "type": content_type,  # "email", "letter", "application"
            "prompt": initial_prompt,
            "answers": {},
            "current_question": None,
            "status": "active"
        }
        
        # Determine questions based on content type
        if content_type == "email":
            questions = [
                "Who should I send this email to? (recipient name/email)",
                "What is the subject of this email?",
                "What is the main purpose or message?",
                "What tone should I use? (formal, casual, professional)",
                "Any specific details or attachments to mention?",
                "When should this be sent? (urgent, by end of day, etc.)"
            ]
        elif content_type == "letter":
            questions = [
                "Who should I address this letter to?",
                "What is the main topic or purpose?",
                "What tone should I use? (formal, business, personal)",
                "Any specific details or requirements?",
                "What is your relationship to the recipient?",
                "Any deadline or urgency mentioned?"
            ]
        elif content_type == "application":
            questions = [
                "What position or opportunity are you applying for?",
                "What is your name and contact information?",
                "What are your key qualifications or experience?",
                "Why are you interested in this opportunity?",
                "What tone should I use? (professional, enthusiastic)",
                "Any specific requirements or attachments needed?"
            ]
        elif content_type == "message":
            questions = [
                "Who should I send this message to?",
                "What is the main purpose or content?",
                "What tone should I use? (casual, formal, friendly)",
                "Any specific details or context to include?",
                "How urgent is this message?",
                "Any specific platform requirements? (SMS, WhatsApp, etc.)"
            ]
        else:
            questions = [
                "What is the main topic or purpose?",
                "Who is the intended audience?",
                "What tone should I use?",
                "Any specific details or requirements?",
                "Any deadline or urgency?"
            ]
        
        session["questions"] = questions
        session["current_question_index"] = 0
        session["current_question"] = questions[0]
        
        self.current_session = session
        self.save_session()
        self.save_current_question()
        
        return f"I'll help you draft a {content_type}. Let me ask you a few questions to get started.\n\n{questions[0]}"
    
    def process_answer(self, answer):
        """Process user's answer and move to next question or generate content"""
        if not self.current_session:
            return "No active drafting session. Please start a new one."
        
        # Save the answer
        current_q = self.current_session["current_question"]
        self.current_session["answers"][current_q] = answer
        
        # Move to next question
        next_index = self.current_session["current_question_index"] + 1
        
        if next_index < len(self.current_session["questions"]):
            # More questions to ask
            self.current_session["current_question_index"] = next_index
            next_question = self.current_session["questions"][next_index]
            self.current_session["current_question"] = next_question
            self.save_session()
            self.save_current_question()
            
            return f"Got it! Next question:\n\n{next_question}"
        else:
            # All questions answered, generate content
            return self.generate_content()
    
    def generate_content(self):
        """Generate the final content based on all answers"""
        if not self.current_session:
            return "No active session to generate content."
        
        # Create a detailed prompt for the AI
        content_type = self.current_session["type"]
        original_prompt = self.current_session["prompt"]
        answers = self.current_session["answers"]
        
        prompt = f"""Create a {content_type} based on the following information:

Original request: {original_prompt}

Details provided:
"""
        
        for question, answer in answers.items():
            prompt += f"- {question}: {answer}\n"
        
        prompt += f"\nPlease create a well-formatted {content_type} that incorporates all these details. Make it professional and appropriate for the specified tone and purpose."
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.7,
                top_p=0.95,
                stream=False
            )
            
            generated_content = completion.choices[0].message.content
            
            # Save the generated content
            with open("Data/generated_content.txt", "w", encoding='utf-8') as f:
                f.write(generated_content)
            
            # End the session
            self.current_session["status"] = "completed"
            self.current_session["generated_content"] = generated_content
            self.save_session()
            
            # Clear current question
            with open(self.questions_file, "w", encoding='utf-8') as f:
                f.write("")
            
            return f"Perfect! I've generated your {content_type}. Here it is:\n\n{generated_content}\n\nI've also saved it to a file for you."
            
        except Exception as e:
            return f"Sorry, I encountered an error while generating the content: {str(e)}"
    
    def get_current_question(self):
        """Get the current question being asked"""
        try:
            with open(self.questions_file, "r", encoding='utf-8') as f:
                return f.read().strip()
        except:
            return ""
    
    def save_current_question(self):
        """Save the current question to file"""
        if self.current_session and self.current_session["current_question"]:
            with open(self.questions_file, "w", encoding='utf-8') as f:
                f.write(self.current_session["current_question"])
    
    def save_session(self):
        """Save the current session to file"""
        if self.current_session:
            with open(self.session_file, "w", encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2)
    
    def load_session(self):
        """Load session from file"""
        try:
            with open(self.session_file, "r", encoding='utf-8') as f:
                self.current_session = json.load(f)
        except:
            self.current_session = None
    
    def cancel_session(self):
        """Cancel the current drafting session"""
        self.current_session = None
        try:
            os.remove(self.session_file)
            os.remove(self.questions_file)
        except:
            pass
        return "Drafting session cancelled."

# Global instance
drafting_system = InteractiveDrafting()

def handle_drafting_request(query):
    """Main function to handle drafting requests"""
    # Load any existing session
    drafting_system.load_session()
    
    # Check if we're in an active session
    if drafting_system.current_session and drafting_system.current_session["status"] == "active":
        # Process as answer to current question
        return drafting_system.process_answer(query)
    
    # Check if this is a new drafting request
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in ["draft", "write", "compose", "create", "prepare"]):
        # Skip email handling - let Gmail integration handle it
        if any(keyword in query_lower for keyword in ["email", "mail", "e-mail"]):
            return None  # Let Gmail integration handle this
        elif any(keyword in query_lower for keyword in ["letter", "application", "cover letter", "cover letter"]):
            content_type = "application" if "application" in query_lower else "letter"
            return drafting_system.start_drafting_session(content_type, query)
        elif any(keyword in query_lower for keyword in ["message", "text", "sms", "whatsapp"]):
            return drafting_system.start_drafting_session("message", query)
        elif any(keyword in query_lower for keyword in ["report", "document", "paper"]):
            return drafting_system.start_drafting_session("document", query)
        else:
            # Default to document for any other drafting request
            return drafting_system.start_drafting_session("document", query)
    
    # Not a drafting request
    return None

def get_current_drafting_question():
    """Get the current drafting question for display"""
    return drafting_system.get_current_question()
