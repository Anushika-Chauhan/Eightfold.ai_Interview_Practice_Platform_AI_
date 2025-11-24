"""
Conversation Management System.
Handles interview flow, question tracking, and persona management.
"""

from typing import List, Dict, Any


class ConversationManager:
    """Manages the interview conversation flow and persona tracking."""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.current_question_idx = 0
        self.questions: List[str] = []
        self.persona_history: List[str] = []  # Track persona changes
    
    def add_answer(self, question: str, answer: str, evaluation: Dict[str, Any] = None, 
                  skipped: bool = False, dont_know: bool = False, is_follow_up: bool = False,
                  original_question: str = None):
        """
        Add an answer to the conversation history.
        
        Args:
            question: The question that was asked
            answer: The candidate's answer
            evaluation: AI evaluation results
            skipped: Whether the question was skipped
            dont_know: Whether the candidate said "I don't know"
            is_follow_up: Whether this was a follow-up question
            original_question: The original question if this is a follow-up
        """
        entry = {
            "question": question,
            "answer": answer,
            "evaluation": evaluation,
            "skipped": skipped,
            "dont_know": dont_know,
            "is_follow_up": is_follow_up,
            "original_question": original_question if is_follow_up else None
        }
        self.history.append(entry)
        
        # Track persona if evaluation available
        if evaluation and "persona" in evaluation:
            self.persona_history.append(evaluation["persona"])
    
    def get_answered_questions(self) -> List[Dict[str, Any]]:
        """Get all answered questions (not skipped)."""
        return [entry for entry in self.history if not entry.get("skipped", False)]
    
    def get_skipped_questions(self) -> List[Dict[str, Any]]:
        """Get all skipped questions."""
        return [entry for entry in self.history if entry.get("skipped", False)]
    
    def get_dont_know_responses(self) -> List[Dict[str, Any]]:
        """Get all "I don't know" responses."""
        return [entry for entry in self.history if entry.get("dont_know", False)]
    
    def get_follow_up_questions(self) -> List[Dict[str, Any]]:
        """Get all follow-up questions."""
        return [entry for entry in self.history if entry.get("is_follow_up", False)]
    
    def get_persona_consistency(self) -> Dict[str, Any]:
        """
        Analyze persona consistency throughout the interview.
        
        Returns:
            Dict with dominant persona, consistency score, and persona distribution
        """
        if not self.persona_history:
            return {
                "dominant_persona": "Not yet determined",
                "consistency_score": 0,
                "persona_distribution": {},
                "message": "Persona will be identified after your first few responses."
            }
        
        # Count persona occurrences
        persona_counts = {}
        for persona in self.persona_history:
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
        
        # Find dominant persona
        dominant_persona = max(persona_counts, key=persona_counts.get)
        total_responses = len(self.persona_history)
        dominant_count = persona_counts[dominant_persona]
        
        # Calculate consistency score (0-100%)
        consistency_score = (dominant_count / total_responses) * 100
        
        # Generate persona-specific message
        if consistency_score >= 80:
            message = f"You consistently demonstrated {dominant_persona} persona traits throughout the interview."
        elif consistency_score >= 60:
            message = f"You primarily showed {dominant_persona} persona traits with some variation."
        else:
            message = "You showed a mix of different persona traits throughout the interview."
        
        # Add specific guidance based on persona
        persona_guidance = {
            "Confused": "Focus on structuring your responses clearly. When unsure, it's okay to ask for clarification or admit knowledge gaps while showing how you'd find the answer.",
            "Efficient": "Your concise responses are valuable, but ensure you're covering key points. Consider adding one relevant example to strengthen your answers.",
            "Chatty": "Your enthusiasm is great, but try to stay focused on the question. Structure your responses with clear points and save personal stories for networking.",
            "Edge Case": "Brief responses can be effective, but make sure they're relevant to the question. Try to provide at least one specific detail or example."
        }
        
        guidance = persona_guidance.get(dominant_persona, "Continue practicing to develop a consistent communication style.")
        
        return {
            "dominant_persona": dominant_persona,
            "consistency_score": round(consistency_score, 1),
            "persona_distribution": persona_counts,
            "message": message,
            "guidance": guidance
        }
    
    def get_dominant_persona(self) -> str:
        """
        Get the most frequently occurring persona.
        
        Returns:
            The dominant persona or "Not yet determined" if no personas tracked
        """
        if not self.persona_history:
            return "Not yet determined"
        
        # Count persona occurrences
        persona_counts = {}
        for persona in self.persona_history:
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
        
        # Return the most common persona
        return max(persona_counts, key=persona_counts.get)
    
    def should_ask_follow_up(self, evaluation: Dict[str, Any]) -> bool:
        """
        Determine if a follow-up question should be asked based on evaluation.
        
        Args:
            evaluation: AI evaluation results
            
        Returns:
            True if follow-up should be asked, False otherwise
        """
        # Check if evaluation suggests follow-up
        if not evaluation:
            return False
            
        # If AI explicitly suggests follow-up
        if evaluation.get("follow_up_suggested", False):
            return True
            
        # If answer shows partial understanding
        overall_score = evaluation.get("overall_score", 0)
        if 5 <= overall_score <= 7:  # Mid-range score suggests partial understanding
            return True
            
        return False
    
    def get_progress_stats(self) -> Dict[str, int]:
        """
        Get interview progress statistics.
        
        Returns:
            Dict with answered, skipped, and total question counts
        """
        answered = len(self.get_answered_questions())
        skipped = len(self.get_skipped_questions())
        total = len(self.history)
        
        return {
            "answered": answered,
            "skipped": skipped,
            "total": total
        }
    
    def get_persona_specific_insights(self) -> Dict[str, str]:
        """
        Get persona-specific insights and recommendations.
        
        Returns:
            Dict with persona-specific insights
        """
        insights = {
            "Efficient": {
                "description": "Short, direct answers that stay on topic with no off-topic content",
                "strengths": "Communicates effectively without unnecessary details",
                "improvements": "Add one specific example or metric to strengthen answers",
                "example_response": "The key concept is X. For example, in my previous project, I implemented Y which resulted in Z improvement."
            },
            "Confused": {
                "description": "Unclear, fragmented, contradictory, or unsure responses with poor structure",
                "strengths": "Shows engagement and willingness to respond",
                "improvements": "Practice structuring responses with clear points, ask clarifying questions when needed",
                "example_response": "I'm not entirely sure about this, but here's what I understand: [provide structured explanation]"
            },
            "Chatty": {
                "description": "Goes off-topic, changes the subject, redirects conversation, or repeats questions",
                "strengths": "Enthusiastic and shows good communication skills",
                "improvements": "Focus on key points first, save stories for later networking",
                "example_response": "The main point is X. To illustrate, [brief relevant example]. This approach has several benefits: 1) A, 2) B, 3) C."
            },
            "Edge Case": {
                "description": "Invalid input, audio unclear/missing, empty answer, or says 'I don't know'",
                "strengths": "Direct and to the point, shows honesty",
                "improvements": "Provide at least one specific detail or example to demonstrate knowledge, or briefly mention related concepts",
                "example_response": "I'm not familiar with this specific concept, but I know it relates to X and Y. To learn more, I would research A, B, and C resources."
            }
        }
        
        return insights