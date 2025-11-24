from utils.ai_evaluator import AIEvaluator

# Test the persona classification
e = AIEvaluator()

# Test regular answer
print("Testing regular answer:")
regular_result = e._fallback_eval("This is a regular answer that is somewhat confused with uh and um", False)
print(f"Regular answer persona: {regular_result.get('persona')}")
print(f"Regular answer score: {regular_result.get('overall_score')}")

# Test follow-up answer
print("\nTesting follow-up answer:")
followup_result = e._fallback_eval("This is a follow-up answer that should be marked as Efficient", True)
print(f"Follow-up answer persona: {followup_result.get('persona')}")
print(f"Follow-up answer score: {followup_result.get('overall_score')}")

# Test Chatty persona
print("\nTesting Chatty persona:")
chatty_result = e._fallback_eval("Let's discuss this topic instead of answering directly. I think it would be more interesting to talk about something else.", False)
print(f"Chatty answer persona: {chatty_result.get('persona')}")
print(f"Chatty answer score: {chatty_result.get('overall_score')}")

# Test Efficient persona
print("\nTesting Efficient persona:")
efficient_result = e._fallback_eval("Specifically, I implemented a REST API using Node.js and Express. I designed the database schema with MongoDB and optimized queries for performance.", False)
print(f"Efficient answer persona: {efficient_result.get('persona')}")
print(f"Efficient answer score: {efficient_result.get('overall_score')}")