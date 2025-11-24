from utils.ai_evaluator import AIEvaluator

# Test the persona classification
e = AIEvaluator()

# Test cases
test_cases = [
    ("Chatty", "Let's discuss this topic instead of answering directly. I think it would be more interesting to talk about something else."),
    ("Efficient", "Specifically, I implemented a REST API using Node.js and Express. I designed the database schema with MongoDB and optimized queries for performance. The system handles 10,000 requests per second with a response time under 200ms."),
    ("Confused with low score", "Uh, I'm not sure about this question. Maybe it's something to do with, um, databases? I think, perhaps, it's about SQL or something like that. I'm a bit confused."),
    ("Confused with high score", "I'm not entirely sure about this specific concept, but I understand it relates to database optimization. In my previous project, I worked with query optimization techniques that improved performance by 30%. I used indexing strategies and query restructuring to achieve these results."),
    ("Edge Case", "I don't know")
]

print("Testing persona classification:")
print("=" * 50)

for test_name, answer in test_cases:
    result = e._fallback_eval(answer)
    detected_persona = result.get('persona', 'Unknown')
    overall_score = result.get('overall_score', 0)
    communication_skills = result.get('communication_skills', 0) if 'communication_skills' in result else result.get('communication_clarity', 0)
    
    print(f"\nTest: {test_name}")
    print(f"Answer: {answer[:50]}...")
    print(f"Detected Persona: {detected_persona}")
    print(f"Overall Score: {overall_score}")
    print(f"Communication Skills Score: {communication_skills}")