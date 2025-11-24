"""
AI Evaluation System.
Handles AI-powered answer evaluation and feedback generation.
"""

import json
import os
from typing import Any, Dict
import streamlit as st
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False


class AIEvaluator:
    """AI evaluation engine."""
    
    def __init__(self):
        self.is_ready = False
        
        # Load API key from .env file first
        load_dotenv()
        self.key = os.getenv("GEMINI_API_KEY")
        
        # Fallback to streamlit secrets if .env not found
        if not self.key:
            try:
                self.key = st.secrets.get("GEMINI_API_KEY")
            except Exception:
                pass
        
        # Fallback to environment variable
        if not self.key:
            self.key = os.environ.get("GEMINI_API_KEY")
        
        if self.key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.key)
                self.client = genai
                # Test the API with a simple request
                test_model = genai.GenerativeModel('gemini-2.0-flash')
                test_response = test_model.generate_content("Say 'API works' in one word")
                if test_response.text and len(test_response.text.strip()) > 0:
                    self.is_ready = True
                    print(f"Gemini API initialized successfully")
                else:
                    raise Exception("API test returned empty response")
            except Exception as e:
                st.error(f"AI init failed: {e}")
                print(f"AI init error: {e}")
    
    def evaluate_technical(self, role: str, question: str, answer: str, persona_history: list = None) -> Dict[str, Any]:
        """
        Evaluate technical interview answer.
        
        Args:
            role: Job role being interviewed for
            question: Question asked
            answer: Candidate's answer
            persona_history: List of previous personas to maintain consistency
        
        Returns:
            Dict with scores, strengths, improvements, persona, follow-up, perfect_answer
        """
        if not self.is_ready:
            return self._fallback_eval(answer)
        
        # Get the current dominant persona if available
        current_persona = ""
        if persona_history:
            # Count persona occurrences
            persona_counts = {}
            for p in persona_history:
                persona_counts[p] = persona_counts.get(p, 0) + 1
            
            # Get the most common persona
            if persona_counts:
                current_persona = max(persona_counts, key=persona_counts.get)
        
        prompt = f"""You are an expert technical interviewer for {role} position with deep industry experience.

Question Asked: {question}
Candidate's Answer: {answer}

Analyze the answer carefully to detect the candidate's persona from their answer style using these STRICT categories:
1. Efficient User: Short, direct answers that stay on topic with no off-topic content and directly address the question
2. Confused User: Unclear, fragmented, contradictory, or unsure responses with poor structure
3. Chatty User: Goes off-topic, changes the subject, redirects conversation, or repeats questions
4. Edge Case User: Invalid input, audio unclear/missing, empty answer, or says 'I don't know'

Use ONLY these four personas. Do NOT default to Confused for everything.

Classification Rules:
- If they ask to repeat the question or say "can you repeat" → Chatty
- If they change the subject or go off-topic → Chatty
- If they express interest in discussing/going over topics rather than answering directly → Chatty
- If they say "move to next topic" or similar phrases like "can we discuss this instead" or "let's talk about something else" or "let's discuss this topic instead" → Chatty
- If they directly address the question with a clear answer:
  * If answer score is above 5 AND directly addresses question → Efficient
  * If answer score is 5 or below OR doesn't directly address question → Confused
- If they ask for a follow-up question or show interest in deeper discussion → Efficient
- Saying 'I don't know' → Edge Case
- Audio not understood/missing → Edge Case

Special Rules:
- If a Confused persona response receives a score above 4, reclassify as Efficient
- If this is a follow-up question response, classify as Efficient

Previous response patterns suggest the candidate tends to be: {current_persona if current_persona else "Not yet determined - observe this response"}

Evaluate the technical content with these personas in mind:
- For Efficient users: Assess depth of knowledge and technical precision despite brevity
- For Confused users: Focus on identifying core knowledge gaps and providing guidance
- For Chatty users: Identify relevant technical points amidst the details, politely redirect to structured answering
- For Edge Case users: Determine if they're being honest about knowledge gaps or if there was a technical issue

Evaluate the technical content thoroughly:
- Does it DIRECTLY answer the question asked?
- Is the technical content accurate and complete?
- Does it show deep understanding of the concept?
- Are examples and specifics provided where appropriate?
- Does it demonstrate practical application knowledge?

Additionally, evaluate communication skills specifically:
- Clarity of expression
- Conciseness without losing important details
- Appropriate use of technical terminology
- Logical flow and structure
- Ability to stay on topic

Provide a comprehensive perfect answer (4-5 lines) that should have been given, including technical details and best practices.
Create a SPECIFIC follow-up question based on what they actually said that tests deeper understanding.

Return ONLY valid JSON in this exact format:
{{
  "technical_accuracy": 0-10,
  "problem_solving": 0-10,
  "depth_of_knowledge": 0-10,
  "communication_clarity": 0-10,
  "communication_skills": 0-10,
  "overall_score": 0-10,
  "strengths": ["2-3 specific strengths based on their actual response"],
  "improvements": ["2-3 specific improvements based on their actual response"],
  "persona": "Efficient/Confused/Chatty/Edge Case",
  "follow_up": "specific follow-up based on their answer that tests deeper understanding",
  "perfect_answer": "comprehensive perfect answer (4-5 lines with complete technical details, examples, and best practices)"
}}

No markdown, just JSON. Ensure all scores are integers between 0-10. Be specific and detailed in your feedback."""
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n```", 1)[0].strip()
            if content.startswith("json"):
                content = content[4:].strip()
            result = json.loads(content)
            return result
        except Exception as e:
            st.error(f"AI evaluation error: {str(e)}")
            st.warning("Using fallback evaluation. Please check your API configuration.")
            return self._fallback_eval(answer)
    
    def evaluate_behavioral(self, role: str, question: str, answer: str, persona_history: list = None) -> Dict[str, Any]:
        """
        Evaluate behavioral/HR interview answer.
        
        Args:
            role: Job role being interviewed for
            question: Question asked
            answer: Candidate's answer
            persona_history: List of previous personas to maintain consistency
        
        Returns:
            Dict with scores, strengths, improvements, persona, follow-up, perfect_answer
        """
        if not self.is_ready:
            return self._fallback_eval(answer)
        
        # Get the current dominant persona if available
        current_persona = ""
        if persona_history:
            # Count persona occurrences
            persona_counts = {}
            for p in persona_history:
                persona_counts[p] = persona_counts.get(p, 0) + 1
            
            # Get the most common persona
            if persona_counts:
                current_persona = max(persona_counts, key=persona_counts.get)
        
        prompt = f"""You are an expert HR interviewer for {role} position with deep industry experience.

Question Asked: {question}
Candidate's Answer: {answer}

Analyze the answer carefully to detect the candidate's persona from their answer style using these STRICT categories:
1. Efficient User: Short, direct answers that stay on topic with no off-topic content and directly address the question
2. Confused User: Unclear, fragmented, contradictory, or unsure responses with poor structure
3. Chatty User: Goes off-topic, changes the subject, redirects conversation, or repeats questions
4. Edge Case User: Invalid input, audio unclear/missing, empty answer, or says 'I don't know'

Use ONLY these four personas. Do NOT default to Confused for everything.

Classification Rules:
- If they ask to repeat the question or say "can you repeat" → Chatty
- If they change the subject or go off-topic → Chatty
- If they express interest in discussing/going over topics rather than answering directly → Chatty
- If they say "move to next topic" or similar phrases like "can we discuss this instead" or "let's talk about something else" or "let's discuss this topic instead" → Chatty
- If they directly address the question with a clear answer:
  * If answer score is above 5 AND directly addresses question → Efficient
  * If answer score is 5 or below OR doesn't directly address question → Confused
- If they ask for a follow-up question or show interest in deeper discussion → Efficient
- Saying 'I don't know' → Edge Case
- Audio not understood/missing → Edge Case

Special Rules:
- If a Confused persona response receives a score above 4, reclassify as Efficient
- If this is a follow-up question response, classify as Efficient

Previous response patterns suggest the candidate tends to be: {current_persona if current_persona else "Not yet determined - observe this response"}

Evaluate the behavioral content with these personas in mind:
- For Efficient users: Assess completeness of STAR examples and cultural fit despite brevity
- For Confused users: Focus on identifying communication gaps and providing guidance
- For Chatty users: Extract relevant behavioral examples from verbose responses, politely redirect to structured answering
- For Edge Case users: Determine if they're being honest about knowledge gaps or if there was a technical issue

Evaluate the behavioral content thoroughly:
- Does it DIRECTLY answer the behavioral question asked?
- Does it use STAR method (Situation, Task, Action, Result)?
- Is it relevant with concrete examples?
- Are the examples specific and demonstrate the required skills?
- Does it show growth, learning, or self-awareness?

Additionally, evaluate communication skills specifically:
- Clarity of expression
- Conciseness without losing important details
- Appropriate use of professional language
- Logical flow and structure
- Ability to stay on topic
- Storytelling effectiveness

Provide a comprehensive perfect answer (4-5 lines) using STAR method with specific details.
Create a SPECIFIC follow-up question based on what they actually said that explores deeper insights.

Return ONLY valid JSON in this exact format:
{{
  "communication_skills": 0-10,
  "teamwork_collaboration": 0-10,
  "leadership_potential": 0-10,
  "cultural_fit": 0-10,
  "overall_score": 0-10,
  "strengths": ["2-3 specific strengths based on their actual response"],
  "improvements": ["2-3 specific improvements based on their actual response"],
  "persona": "Efficient/Confused/Chatty/Edge Case",
  "follow_up": "specific follow-up based on their answer that explores deeper insights",
  "perfect_answer": "comprehensive perfect STAR answer (4-5 lines with complete example, specific details, and outcomes)"
}}

No markdown, just JSON. Ensure all scores are integers between 0-10. Be specific and detailed in your feedback."""
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n```", 1)[0].strip()
            if content.startswith("json"):
                content = content[4:].strip()
            result = json.loads(content)
            return result
        except Exception as e:
            st.error(f"AI evaluation error: {str(e)}")
            st.warning("Using fallback evaluation. Please check your API configuration.")
            return self._fallback_eval(answer)
    
    def _fallback_eval(self, answer: str, is_follow_up: bool = False) -> Dict[str, Any]:
        """Fallback evaluation when AI is unavailable."""
        answer_lower = (answer or "").lower()
        words = answer_lower.split()
        length = len(words)
        
        # NEW: If this is a follow-up question, classify as Efficient
        if is_follow_up:
            persona = "Efficient"
        else:
            # Detect if user just repeated the question or went off-topic
            question_keywords = ["tell me", "describe", "explain", "how would you", "what is", "can you", "could you", "repeat the question", "ask again", "say that again", "can you repeat"]
            is_question_repeat = any(kw in answer_lower for kw in question_keywords)
            
            # Detect if user wants to discuss rather than answer
            discussion_keywords = ["can we discuss", "let's talk about", "rather than", "instead of", "going over", "talk about", "discuss this", "what do you think about", "let's discuss this topic instead"]
            wants_discussion = any(kw in answer_lower for kw in discussion_keywords)
            
            # Detect if user wants to move to next topic
            next_topic_keywords = ["move to next", "next topic", "change topic", "different topic", "skip this", "let's move on", "can we move on", "let's discuss something else", "can we talk about something else"]
            wants_next_topic = any(kw in answer_lower for kw in next_topic_keywords)
            
            # Enhanced persona detection with strict rules
            if "i don't know" in answer_lower or "i dont know" in answer_lower or "i'm not sure" in answer_lower or "im not sure" in answer_lower or length == 0:
                persona = "Edge Case"  # "I don't know" or empty response
            elif is_question_repeat or "another question" in answer_lower or "different question" in answer_lower or "repeat" in answer_lower or wants_discussion or wants_next_topic:
                persona = "Chatty"  # Redirecting, repeating the question, wanting discussion, or wanting to move topics
            elif length > 150:  # Very long response
                persona = "Chatty"  # Likely off-topic or rambling
            elif length < 5 and length > 0:
                # Very short response, check if it's a clear answer or just filler
                clear_answer_indicators = ["yes", "no", "definitely", "certainly", "absolutely", "specifically", "exactly", "indeed", "correct", "true", "false"]
                if any(indicator in answer_lower for indicator in clear_answer_indicators) or length >= 3:
                    persona = "Efficient"  # Short but clear response
                else:
                    persona = "Confused"  # Too short to be meaningful
            else:
                # For other cases, we'll determine based on content quality
                # Check for confused indicators
                confused_indicators = ["uhh", "umm", "i think", "maybe", "i guess", "not sure", "confused", "unclear", "i'm lost", "don't understand", "i don't know", "i am lost", "cannot understand"]
                is_confused = any(indicator in answer_lower for indicator in confused_indicators)
                
                # Check for chatty indicators (filler words, hesitations)
                chatty_indicators = ["well", "you know", "like", "um", "uh", "er", "ah", "actually", "basically", "literally", "totally", "honestly", "frankly", "to be honest", "in my opinion", "i mean", "kind of", "sort of"]
                chatty_count = sum(1 for indicator in chatty_indicators if indicator in answer_lower)
                
                if is_confused and chatty_count < 2:
                    persona = "Confused"  # Clear confusion indicators
                elif chatty_count >= 3 or (chatty_count >= 2 and length > 50):
                    persona = "Chatty"  # Too many filler words or long with fillers
                else:
                    # Check for efficient indicators (clear, direct language)
                    efficient_indicators = ["specifically", "exactly", "directly", "clearly", "precisely", "effectively", "efficiently", "first", "second", "third", "finally", "in summary", "to conclude", "therefore", "consequently", "as a result", "thus", "hence"]
                    efficient_count = sum(1 for indicator in efficient_indicators if indicator in answer_lower)
                    
                    # If the response has efficient language or structured format, mark as Efficient
                    if efficient_count >= 2 or any(phrase in answer_lower for phrase in ["in summary", "to conclude", "first", "second", "therefore", "consequently"]):
                        persona = "Efficient"
                    # If response is reasonably long and coherent with technical terms, mark as Efficient
                    elif length >= 20 and efficient_count >= 1:
                        persona = "Efficient"
                    # If response is short but clear and direct, mark as Efficient
                    elif length < 20 and not is_confused and chatty_count < 2:
                        persona = "Efficient"
                    else:
                        persona = "Confused"  # Default to confused for unclear cases
        
        # Enhanced scoring based on content quality indicators
        quality_indicators = ["example", "situation", "result", "task", "action", "implemented", "designed", "developed", "improved", "resolved", "specifically", "exactly", "first", "second", "finally", "increased", "decreased", "reduced", "enhanced", "optimized"]
        quality_count = sum(1 for indicator in quality_indicators if indicator in answer_lower)
        
        # Communication quality indicators
        communication_indicators = ["clearly", "concisely", "effectively", "collaborated", "communicated", "explained", "presented", "discussed", "articulated", "expressed"]
        communication_count = sum(1 for indicator in communication_indicators if indicator in answer_lower)
        
        # Persona-specific scoring with enhanced communication evaluation
        if persona == "Confused":
            # Confused persona - provide guidance
            score = max(1, min(10, int(length / 2) + quality_count))
            # NEW: If confused persona has a score above 4, mark as Efficient
            if score > 4:
                persona = "Efficient"
                final_score = score
                communication_clarity = min(10, score + 2)
                communication_skills = min(10, score + 2)
            else:
                final_score = score
                communication_clarity = max(1, score - 2)  # Penalty for clarity issues
                communication_skills = max(2, score - 1)  # Some credit for attempting communication
            
            if persona == "Efficient":  # After reclassification
                return {
                    "technical_accuracy": min(10, final_score + 1),
                    "problem_solving": final_score,
                    "depth_of_knowledge": final_score,
                    "communication_clarity": communication_clarity,
                    "communication_skills": communication_skills,
                    "teamwork_collaboration": final_score,
                    "leadership_potential": final_score,
                    "cultural_fit": final_score,
                    "overall_score": final_score,
                    "strengths": ["Clear and concise response", "Directly addresses the question", "Good communication"],
                    "improvements": ["Add more technical details and examples" if final_score < 7 else "Include specific metrics or outcomes", "Provide concrete examples"],
                    "persona": persona,
                    "follow_up": "Can you elaborate on one key point with a specific example?",
                    "perfect_answer": "A comprehensive answer should include specific technical details, examples with metrics, and outcomes. For example: 'In my previous project, I implemented X solution which resulted in Y improvement by Z%. This involved A, B, and C technical considerations.'"
                }
            else:  # Still Confused
                return {
                    "technical_accuracy": final_score,
                    "problem_solving": final_score,
                    "depth_of_knowledge": final_score,
                    "communication_clarity": communication_clarity,  # Penalty for clarity issues
                    "communication_skills": communication_skills,  # Some credit for attempting communication
                    "teamwork_collaboration": final_score,
                    "leadership_potential": final_score,
                    "cultural_fit": final_score,
                    "overall_score": final_score,
                    "strengths": ["Attempted to respond", "Showed engagement"],
                    "improvements": ["Answer the question directly", "Provide specific examples", "Use the STAR method for structured responses"],
                    "persona": persona,
                    "follow_up": "Can you share a specific situation from your experience?",
                    "perfect_answer": "Please provide a real example from your experience using the STAR method (Situation, Task, Action, Result) with specific details and outcomes."
                }
        
        elif persona == "Chatty":
            # Chatty users might have good content but need to be more concise
            score = max(3, min(10, int(length / 20) + quality_count + communication_count))
            return {
                "technical_accuracy": max(2, score - 2),  # Possible penalty for lack of focus
                "problem_solving": score,
                "depth_of_knowledge": max(2, score - 1),  # Possible penalty for lack of depth
                "communication_clarity": max(1, score - 3),  # Penalty for verbosity
                "communication_skills": max(4, score),  # Credit for communication ability
                "teamwork_collaboration": min(10, score + 2),  # Bonus for collaborative communication
                "leadership_potential": score,
                "cultural_fit": min(10, score + 1),
                "overall_score": score,
                "strengths": ["Enthusiastic response", "Good communication"],
                "improvements": ["Focus on key points and be more concise", "Stay on topic", "Structure your response with clear sections"],
                "persona": persona,
                "follow_up": "Can you summarize your main points in 2-3 sentences?",
                "perfect_answer": "A well-structured answer should include specific details, examples with metrics, and outcomes. Use the STAR method: Situation, Task, Action, Result with concrete details. Keep it focused and concise."
            }
        
        elif persona == "Edge Case":
            # Edge case responses get minimal scores
            score = 0
            return {
                "technical_accuracy": score,
                "problem_solving": score,
                "depth_of_knowledge": score,
                "communication_clarity": score,
                "communication_skills": max(1, score + 1),  # Minimal credit for honesty
                "teamwork_collaboration": score,
                "leadership_potential": score,
                "cultural_fit": score,
                "overall_score": score,
                "strengths": ["Honesty in acknowledging knowledge gaps"],
                "improvements": ["Try to provide partial knowledge or related experience even when unsure"],
                "persona": persona,
                "follow_up": "Can you tell me about a time you encountered a knowledge gap and how you addressed it?",
                "perfect_answer": "When you're unsure about something, it's better to acknowledge it honestly but also mention related knowledge or how you would find the answer."
            }
        
        else:  # Efficient
            # Efficient users get standard scoring with communication bonuses
            score = max(5, min(10, int(length / 4) + quality_count + communication_count + 2))  # Bonus for efficiency
            return {
                "technical_accuracy": min(10, score + 1),
                "problem_solving": score,
                "depth_of_knowledge": score,
                "communication_clarity": min(10, score + 2),  # Bonus for clear communication
                "communication_skills": min(10, score + 2),  # Bonus for good communication
                "teamwork_collaboration": score,
                "leadership_potential": score,
                "cultural_fit": score,
                "overall_score": score,
                "strengths": ["Clear and concise response", "Directly addresses the question", "Good communication"],
                "improvements": ["Add more technical details and examples" if score < 7 else "Include specific metrics or outcomes", "Provide concrete examples"],
                "persona": persona,
                "follow_up": "Can you elaborate on one key point with a specific example?",
                "perfect_answer": "A comprehensive answer should include specific technical details, examples with metrics, and outcomes. For example: 'In my previous project, I implemented X solution which resulted in Y improvement by Z%. This involved A, B, and C technical considerations.'"
            }
    
    def generate_question(self, role: str, round_type: str, question_history: list = None) -> str:
        """
        Generate a dynamic interview question based on role and round type.
        
        Args:
            role: Job role being interviewed for
            round_type: Type of interview round (Technical or Behavioral)
            question_history: List of previously asked questions to avoid repetition
        
        Returns:
            Generated question string
        """
        if not self.is_ready:
            # Fallback questions organized by role categories
            role_categories = {
                # Technical roles
                "Software Engineer": {
                    "Technical": [
                        "Explain the difference between object-oriented and functional programming.",
                        "How would you optimize a slow-performing database query?",
                        "Describe the MVC architectural pattern and its benefits.",
                        "What are the key principles of RESTful API design?",
                        "Explain how you would implement a caching strategy for a web application.",
                        "How do you handle memory leaks in a long-running application?",
                        "Describe the differences between SQL and NoSQL databases.",
                        "What are the best practices for securing a web application?",
                        "How would you design a scalable microservices architecture?",
                        "Explain the concept of continuous integration and deployment."
                    ],
                    "Behavioral": [
                        "Tell me about a time you had to debug a complex issue under tight deadlines.",
                        "Describe a situation where you had to learn a new technology quickly.",
                        "Tell me about a time you had to refactor legacy code.",
                        "Describe a situation where you had to collaborate with a difficult team member.",
                        "Tell me about a time you made a mistake in production and how you handled it.",
                        "Describe a situation where you had to make a trade-off between speed and quality.",
                        "Tell me about a time you went above and beyond to solve a technical problem.",
                        "Describe a situation where you had to explain a complex technical concept to a non-technical stakeholder.",
                        "Tell me about a time you had to resolve a conflict within your development team.",
                        "Describe a situation where you demonstrated leadership in a technical project."
                    ]
                },
                "Data Scientist": {
                    "Technical": [
                        "Explain the bias-variance tradeoff in machine learning.",
                        "How would you handle missing data in a dataset?",
                        "Describe the difference between supervised and unsupervised learning.",
                        "What are the key steps in a typical data science project lifecycle?",
                        "Explain how you would evaluate the performance of a classification model.",
                        "How do you deal with overfitting in machine learning models?",
                        "Describe the process of feature engineering and its importance.",
                        "What are the assumptions of linear regression?",
                        "How would you approach an A/B testing experiment?",
                        "Explain the concept of cross-validation and why it's important."
                    ],
                    "Behavioral": [
                        "Tell me about a time you had to present complex data findings to stakeholders.",
                        "Describe a situation where your analysis challenged existing business assumptions.",
                        "Tell me about a time you had to work with incomplete or messy data.",
                        "Describe a situation where you had to collaborate with domain experts.",
                        "Tell me about a time you had to explain statistical concepts to non-technical colleagues.",
                        "Describe a situation where you had to pivot your analysis approach midway.",
                        "Tell me about a time you identified a critical insight that others missed.",
                        "Describe a situation where you had to defend your analytical methodology.",
                        "Tell me about a time you had to balance accuracy with business needs.",
                        "Describe a situation where you demonstrated leadership in a data science project."
                    ]
                },
                "Frontend Engineer": {
                    "Technical": [
                        "Explain the difference between server-side rendering and client-side rendering.",
                        "How would you optimize the performance of a web application?",
                        "Describe the concept of component-based architecture.",
                        "What are the key principles of responsive web design?",
                        "Explain how you would implement state management in a large application.",
                        "How do you ensure cross-browser compatibility in your projects?",
                        "Describe the difference between CSS Grid and Flexbox.",
                        "What are the best practices for accessibility in web development?",
                        "How would you handle state synchronization between multiple components?",
                        "Explain the concept of progressive web apps and their benefits."
                    ],
                    "Behavioral": [
                        "Tell me about a time you had to balance user experience with technical constraints.",
                        "Describe a situation where you had to advocate for the user in a design discussion.",
                        "Tell me about a time you had to learn a new frontend framework quickly.",
                        "Describe a situation where you had to collaborate closely with designers.",
                        "Tell me about a time you had to refactor a legacy frontend codebase.",
                        "Describe a situation where you had to handle conflicting feedback from stakeholders.",
                        "Tell me about a time you went above and beyond to improve user experience.",
                        "Describe a situation where you had to explain frontend limitations to non-technical team members.",
                        "Tell me about a time you had to resolve a conflict with a designer or product manager.",
                        "Describe a situation where you demonstrated leadership in a frontend project."
                    ]
                },
                "DevOps Engineer": {
                    "Technical": [
                        "Explain the concept of Infrastructure as Code and its benefits.",
                        "How would you design a CI/CD pipeline for a microservices architecture?",
                        "Describe the key principles of container orchestration.",
                        "What are the best practices for monitoring and logging in distributed systems?",
                        "Explain how you would ensure high availability and fault tolerance.",
                        "How do you handle secrets management in a cloud environment?",
                        "Describe the difference between blue-green deployment and rolling deployment.",
                        "What are the key considerations for cloud cost optimization?",
                        "How would you approach disaster recovery planning?",
                        "Explain the concept of chaos engineering and its purpose."
                    ],
                    "Behavioral": [
                        "Tell me about a time you had to resolve a critical production incident.",
                        "Describe a situation where you had to convince the team to adopt new DevOps practices.",
                        "Tell me about a time you had to balance security with development speed.",
                        "Describe a situation where you had to collaborate with development teams.",
                        "Tell me about a time you had to explain complex infrastructure issues to management.",
                        "Describe a situation where you had to work under extreme pressure during an outage.",
                        "Tell me about a time you automated a manual process that saved significant time.",
                        "Describe a situation where you had to prioritize competing infrastructure demands.",
                        "Tell me about a time you had to resolve a conflict between development and operations teams.",
                        "Describe a situation where you demonstrated leadership in improving system reliability."
                    ]
                },
                "Product Manager": {
                    "Technical": [
                        "How would you prioritize features in a product roadmap?",
                        "Describe the process of conducting market research for a new product.",
                        "What metrics would you use to measure product success?",
                        "Explain how you would handle conflicting requirements from stakeholders.",
                        "How do you validate product ideas before development?",
                        "Describe the difference between KPIs and vanity metrics.",
                        "How would you approach A/B testing for a new feature?",
                        "What are the key elements of a successful product launch?",
                        "Explain the concept of minimum viable product (MVP).",
                        "How do you handle scope creep in a product development cycle?"
                    ],
                    "Behavioral": [
                        "Tell me about a time you had to make a difficult product decision with limited data.",
                        "Describe a situation where you had to influence stakeholders without formal authority.",
                        "Tell me about a time you had to pivot product strategy based on user feedback.",
                        "Describe a situation where you had to manage competing priorities from different teams.",
                        "Tell me about a time you had to deliver bad news to stakeholders.",
                        "Describe a situation where you had to balance user needs with business objectives.",
                        "Tell me about a time you went above and beyond to understand customer needs.",
                        "Describe a situation where you had to resolve a conflict between engineering and business teams.",
                        "Tell me about a time you had to justify a product decision to senior leadership.",
                        "Describe a situation where you demonstrated leadership in driving product vision."
                    ]
                },
                "UX Designer": {
                    "Technical": [
                        "Describe your design process from research to implementation.",
                        "How would you conduct a usability test for a new feature?",
                        "Explain the difference between user research and market research.",
                        "What are the key principles of inclusive design?",
                        "How do you approach designing for mobile vs desktop experiences?",
                        "Describe the concept of design systems and their benefits.",
                        "How would you handle feedback that contradicts your design decisions?",
                        "What methods do you use to validate design concepts with users?",
                        "Explain the difference between wireframes, mockups, and prototypes.",
                        "How do you ensure consistency across different parts of a product?"
                    ],
                    "Behavioral": [
                        "Tell me about a time you had to advocate for user needs against business pressures.",
                        "Describe a situation where user research changed your design approach.",
                        "Tell me about a time you had to collaborate with developers who challenged your designs.",
                        "Describe a situation where you had to present design rationale to stakeholders.",
                        "Tell me about a time you received harsh criticism on your designs.",
                        "Describe a situation where you had to balance creativity with practicality.",
                        "Tell me about a time you went above and beyond to understand user pain points.",
                        "Describe a situation where you had to resolve a design conflict within your team.",
                        "Tell me about a time you had to educate stakeholders about UX principles.",
                        "Describe a situation where you demonstrated leadership in improving user experience."
                    ]
                },
                "Data Analyst": {
                    "Technical": [
                        "How would you approach analyzing a large dataset to identify trends?",
                        "Explain the difference between descriptive and inferential statistics.",
                        "What are the key steps in data cleaning and preprocessing?",
                        "How do you choose the right visualization for different types of data?",
                        "Describe how you would validate the accuracy of your analysis.",
                        "What are the common pitfalls in data interpretation?",
                        "How would you handle outliers in a dataset?",
                        "Explain the concept of correlation vs causation.",
                        "What tools and techniques do you use for data storytelling?",
                        "How do you ensure your analysis is reproducible and well-documented?"
                    ],
                    "Behavioral": [
                        "Tell me about a time your analysis influenced a major business decision.",
                        "Describe a situation where you had to explain complex findings to non-technical stakeholders.",
                        "Tell me about a time you discovered an error in your analysis after sharing it.",
                        "Describe a situation where you had to work with incomplete or ambiguous requirements.",
                        "Tell me about a time you had to defend your analytical approach.",
                        "Describe a situation where you had to balance accuracy with delivery speed.",
                        "Tell me about a time you went above and beyond to uncover insights.",
                        "Describe a situation where you had to collaborate with cross-functional teams.",
                        "Tell me about a time you had to present findings that challenged existing assumptions.",
                        "Describe a situation where you demonstrated leadership in driving data-driven decisions."
                    ]
                },
                "Sales Representative": {
                    "Technical": [
                        "How do you research prospects before reaching out to them?",
                        "Describe your approach to handling objections during a sales call.",
                        "What metrics do you track to measure your sales performance?",
                        "Explain how you would qualify a sales lead.",
                        "How do you tailor your pitch to different types of customers?",
                        "Describe the key elements of a successful sales presentation.",
                        "How do you handle rejection in sales?",
                        "What strategies do you use to build long-term customer relationships?",
                        "Explain how you would close a deal with a hesitant prospect.",
                        "How do you stay motivated during slow sales periods?"
                    ],
                    "Behavioral": [
                        "Tell me about a time you exceeded your sales targets.",
                        "Describe a situation where you lost a deal and what you learned from it.",
                        "Tell me about a time you had to adapt your sales approach for a difficult client.",
                        "Describe a situation where you had to collaborate with other departments to close a deal.",
                        "Tell me about a time you had to handle a dissatisfied customer.",
                        "Describe a situation where you had to work under intense pressure to meet quotas.",
                        "Tell me about a time you went above and beyond to retain a customer.",
                        "Describe a situation where you had to negotiate a complex contract.",
                        "Tell me about a time you had to resolve a conflict with a colleague over leads.",
                        "Describe a situation where you demonstrated leadership in mentoring junior sales reps."
                    ]
                }
            }
            
            # Default to general questions if role not found
            if role not in role_categories:
                role = "Software Engineer"
            
            # Get questions for the role and round type
            questions = role_categories[role].get(round_type, role_categories[role]["Technical"])
            
            # Filter out already asked questions
            if question_history:
                available_questions = [q for q in questions if q not in question_history]
                if available_questions:
                    questions = available_questions
            
            # Return a random question
            import random
            return random.choice(questions) if questions else "Can you tell me about your experience?"
        
        # AI-generated questions
        history_text = "\n".join(question_history) if question_history else "None"
        
        if round_type == "Technical":
            prompt = f"""You are an expert technical interviewer for {role} position.
            
            Generate a unique technical interview question for this role.
            Avoid repeating these previously asked questions:
            {history_text}
            
            The question should test core technical knowledge for a {role}.
            Make it specific and relevant to the role.
            Keep the question concise and clear (under 15 words).
            
            Return ONLY the question text, nothing else."""
        else:
            prompt = f"""You are an expert HR interviewer for {role} position.
            
            Generate a unique behavioral interview question for this role.
            Avoid repeating these previously asked questions:
            {history_text}
            
            The question should assess soft skills, teamwork, and cultural fit.
            Make it specific and relevant to the role.
            Keep the question concise and clear (under 15 words).
            
            Return ONLY the question text, nothing else."""
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            question = response.text.strip()
            
            # Remove any markdown or extra formatting
            if question.startswith("\"") and question.endswith("\""):
                question = question[1:-1]
            
            return question if question else f"Can you tell me about your experience as a {role}?"
        except Exception as e:
            st.warning(f"Using fallback question generation due to error: {str(e)}")
            # Fallback to static questions
            return self.generate_question(role, round_type, question_history)