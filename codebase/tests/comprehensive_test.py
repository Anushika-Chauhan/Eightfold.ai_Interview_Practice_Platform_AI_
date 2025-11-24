"""
Comprehensive Test Suite for AI Interview Partner
Tests all personas, roles, and evaluation criteria
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.ai_evaluator import AIEvaluator
from config.roles import ROLES
from config.questions import load_questions

def test_all_personas():
    """Test persona detection for all personas with sample responses."""
    print("Testing All Personas")
    print("=" * 50)
    
    # Sample responses for each persona
    test_responses = {
        "Confused": [
            "Um, I'm not sure... maybe it's something about... uh...",
            "I don't know exactly, but I think...",
            "Could you clarify what you mean?",
            "I'm confused about this question."
        ],
        "Efficient": [
            "I use SOLID principles: Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.",
            "Three approaches: Binary Search (O(log n)), Hash Table lookup (O(1)), or Linear Search (O(n)).",
            "Implemented using Redis for caching, reduced API calls by 80%, improved response time from 2s to 200ms."
        ],
        "Chatty": [
            "Well, that's a great question! Let me tell you about this one time at my previous company where we had a similar situation. So basically, we were working on this huge project, and the team was amazing, and we had this really cool architecture. Anyway, to answer your question, I think that...",
            "Oh wow, I love talking about this! So back in college, I learned about this concept, and then when I started working, I applied it differently. My mentor always said that... but I also read this book that said... and honestly, from my experience..."
        ],
        "Edge-Case": [
            "",  # Empty response
            "a",  # Single character
            "No.",  # Very short
            "123456789",  # Numbers only
        ]
    }
    
    evaluator = AIEvaluator()
    
    for persona, responses in test_responses.items():
        print(f"\n--- Testing {persona} Persona ---")
        for i, response in enumerate(responses[:2]):  # Test first 2 responses
            print(f"\nResponse {i+1}: {response[:50]}...")
            if evaluator.is_ready:
                # Test with a sample technical question
                evaluation = evaluator.evaluate_technical(
                    "Software Engineer", 
                    "Explain the difference between processes and threads.", 
                    response
                )
                print(f"Detected Persona: {evaluation.get('persona', 'Unknown')}")
                print(f"Overall Score: {evaluation.get('overall_score', 0)}/10")
                if evaluation.get('strengths'):
                    print(f"Strengths: {', '.join(evaluation['strengths'])}")
                if evaluation.get('improvements'):
                    print(f"Improvements: {', '.join(evaluation['improvements'])}")
            else:
                # Use fallback evaluation
                evaluation = evaluator._fallback_eval(response)
                print(f"Detected Persona: {evaluation.get('persona', 'Unknown')}")
                print(f"Overall Score: {evaluation.get('overall_score', 0)}/10")
                if evaluation.get('strengths'):
                    print(f"Strengths: {', '.join(evaluation['strengths'])}")
                if evaluation.get('improvements'):
                    print(f"Improvements: {', '.join(evaluation['improvements'])}")

def test_all_roles():
    """Test questions for all 8 roles."""
    print("\n\nTesting All Roles")
    print("=" * 50)
    
    questions = load_questions()
    
    for role in ROLES:
        print(f"\n--- {role} ---")
        role_questions = questions.get(role, {})
        for round_type, qs in role_questions.items():
            print(f"  {round_type}: {len(qs)} questions")
            if qs:
                print(f"    Sample: {qs[0][:100]}...")

def test_evaluation_criteria():
    """Test that all evaluation criteria are working."""
    print("\n\nTesting Evaluation Criteria")
    print("=" * 50)
    
    # Test technical evaluation
    evaluator = AIEvaluator()
    
    if evaluator.is_ready:
        tech_eval = evaluator.evaluate_technical(
            "Software Engineer",
            "Design a URL shortening service like bit.ly. Discuss architecture, database schema, and scalability.",
            "I'd design this using a microservices architecture with API Gateway, shortening service using base62 encoding, PostgreSQL for mappings, Redis cache, and horizontal scaling with load balancer."
        )
        
        print("\n--- Technical Evaluation ---")
        print(f"Overall Score: {tech_eval.get('overall_score', 0)}/10")
        print(f"Technical Accuracy: {tech_eval.get('technical_accuracy', 0)}/10")
        print(f"Problem Solving: {tech_eval.get('problem_solving', 0)}/10")
        print(f"Depth of Knowledge: {tech_eval.get('depth_of_knowledge', 0)}/10")
        print(f"Communication Clarity: {tech_eval.get('communication_clarity', 0)}/10")
        print(f"Detected Persona: {tech_eval.get('persona', 'Unknown')}")
        
        # Test behavioral evaluation
        beh_eval = evaluator.evaluate_behavioral(
            "Product Manager",
            "Tell me about a time you had to manage competing priorities.",
            "In my previous role, I had to balance multiple projects with tight deadlines. I prioritized based on business impact and communicated regularly with stakeholders to manage expectations."
        )
        
        print("\n--- Behavioral Evaluation ---")
        print(f"Overall Score: {beh_eval.get('overall_score', 0)}/10")
        print(f"Communication Skills: {beh_eval.get('communication_skills', 0)}/10")
        print(f"Teamwork & Collaboration: {beh_eval.get('teamwork_collaboration', 0)}/10")
        print(f"Leadership Potential: {beh_eval.get('leadership_potential', 0)}/10")
        print(f"Cultural Fit: {beh_eval.get('cultural_fit', 0)}/10")
        print(f"Detected Persona: {beh_eval.get('persona', 'Unknown')}")
    else:
        print("AI not available, using fallback evaluation")
        # Test fallback evaluation
        fallback_eval = evaluator._fallback_eval("This is a sample response for testing purposes.")
        print(f"Fallback Evaluation Score: {fallback_eval.get('overall_score', 0)}/10")
        print(f"Fallback Evaluation Persona: {fallback_eval.get('persona', 'Unknown')}")

if __name__ == "__main__":
    print("AI Interview Partner - Comprehensive Test Suite")
    print("This script tests all personas, roles, and evaluation criteria.")
    
    test_all_personas()
    test_all_roles()
    test_evaluation_criteria()
    
    print("\n\nTest suite completed!")