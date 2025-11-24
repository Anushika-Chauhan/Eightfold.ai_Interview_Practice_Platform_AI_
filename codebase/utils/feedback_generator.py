"""
Feedback Generation System.
Creates visual feedback reports and performance analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any


class FeedbackGenerator:
    """Generates visual feedback and performance reports."""
    
    @staticmethod
    def generate_final_report(history: List[Dict[str, Any]], role: str, interview_type: str):
        """
        Generate comprehensive final interview report.
        
        Args:
            history: Interview history with questions, answers, and evaluations
            role: Job role being interviewed for
            interview_type: Type of interview (Technical, Behavioral, etc.)
        """
        # Filter out skipped questions for analysis
        answered_questions = [q for q in history if not q.get("skipped", False)]
        
        if not answered_questions:
            st.warning("No questions were answered. No feedback to generate.")
            return
        
        # Header
        st.subheader(f"📊 {role} - {interview_type} Interview Report")
        
        # Overall Performance Summary
        st.markdown("### Overall Performance")
        FeedbackGenerator._generate_overall_performance(answered_questions)
        
        st.markdown("---")
        
        # Persona Analysis
        st.markdown("### Persona Analysis")
        FeedbackGenerator._generate_persona_analysis(answered_questions)
        
        st.markdown("---")
        
        # Detailed Question Feedback
        st.markdown("### Detailed Question Feedback")
        FeedbackGenerator._generate_detailed_feedback(answered_questions)
        
        st.markdown("---")
        
        # Performance Trends
        st.markdown("### Performance Trends")
        FeedbackGenerator._generate_performance_trends(answered_questions)
    
    @staticmethod
    def _generate_overall_performance(answered_questions: List[Dict[str, Any]]):
        """Generate overall performance metrics."""
        if not answered_questions:
            st.info("No answered questions to analyze.")
            return
        
        # Calculate overall scores
        total_score = 0
        communication_total = 0
        score_count = 0
        communication_count = 0
        
        # Collect all scores for visualization
        scores = []
        communication_scores = []
        question_numbers = []
        
        for i, entry in enumerate(answered_questions, 1):
            evaluation = entry.get("evaluation", {})
            if evaluation and "overall_score" in evaluation:
                score = evaluation["overall_score"]
                total_score += score
                score_count += 1
                scores.append(score)
                question_numbers.append(f"Q{i}")
                
                # Collect communication skills scores
                if "communication_skills" in evaluation:
                    communication_total += evaluation["communication_skills"]
                    communication_count += 1
                    communication_scores.append(evaluation["communication_skills"])
        
        if score_count > 0:
            avg_score = total_score / score_count
            avg_communication = communication_total / communication_count if communication_count > 0 else 0
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Questions Answered", len(answered_questions))
            col2.metric("Average Score", f"{avg_score:.1f}/10")
            col3.metric("Performance Level", FeedbackGenerator._get_performance_level(avg_score))
            if communication_count > 0:
                col4.metric("Communication Skills", f"{avg_communication:.1f}/10")
            
            # Score distribution chart
            if scores:
                fig = px.bar(
                    x=question_numbers,
                    y=scores,
                    labels={"x": "Question", "y": "Score (0-10)"},
                    title="Score Distribution Across Questions"
                )
                fig.update_layout(yaxis_range=[0, 10])
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No scores available for analysis.")
    
    @staticmethod
    def _get_performance_level(score: float) -> str:
        """Convert numerical score to performance level description."""
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Average"
        else:
            return "Needs Improvement"
    
    @staticmethod
    def _generate_persona_analysis(answered_questions: List[Dict[str, Any]]):
        """Generate persona analysis and consistency report."""
        if not answered_questions:
            st.info("No answered questions to analyze for persona.")
            return
        
        # Collect personas
        personas = []
        for entry in answered_questions:
            evaluation = entry.get("evaluation", {})
            if evaluation and "persona" in evaluation:
                personas.append(evaluation["persona"])
        
        if not personas:
            st.info("Persona analysis will be available after AI evaluation.")
            return
        
        # Count persona occurrences
        persona_counts = {}
        for persona in personas:
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
        
        # Find dominant persona
        dominant_persona = max(persona_counts, key=persona_counts.get)
        total_responses = len(personas)
        dominant_count = persona_counts[dominant_persona]
        
        # Calculate consistency score
        consistency_score = (dominant_count / total_responses) * 100
        
        # Display persona analysis
        st.info(f"**Dominant Persona:** {dominant_persona}")
        st.info(f"**Persona Consistency:** {consistency_score:.1f}%")
        
        # Persona distribution chart
        if len(persona_counts) > 1:
            fig = px.pie(
                values=list(persona_counts.values()),
                names=list(persona_counts.keys()),
                title="Persona Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Persona-specific insights
        persona_insights = {
            "Efficient": "You provided clear, concise responses that directly addressed the questions. This shows strong communication skills and subject matter expertise.",
            "Confused": "Some of your responses indicated uncertainty. This is normal in interviews - focus on asking clarifying questions when needed.",
            "Chatty": "You provided detailed responses with lots of context. While this shows enthusiasm, try to be more concise and focus on key points.",
            "Edge Case": "Your responses were very brief or indicated knowledge gaps. Try to provide more context and examples to demonstrate your knowledge fully."
        }
        
        insight = persona_insights.get(dominant_persona, "Your communication style shows a mix of different approaches.")
        st.info(f"**Insight:** {insight}")
        
        # Special handling for specific scenarios
        st.markdown("#### Persona-Specific Guidance")
        
        # Efficient persona guidance
        if "Efficient" in personas:
            with st.expander("✅ Efficient Persona Guidance"):
                st.markdown("**Characteristics:** Short, direct answers that stay on topic with no off-topic content")
                st.markdown("**Strengths:** Communicates effectively without unnecessary details")
                st.markdown("**Improvements:** Add one specific example or metric to strengthen answers")
                st.markdown("**Example Response:** The key concept is X. For example, in my previous project, I implemented Y which resulted in Z improvement.")
        
        # Confused persona guidance
        if "Confused" in personas:
            with st.expander("❓ Confused Persona Guidance"):
                st.markdown("**Characteristics:** Unclear, fragmented, contradictory, or unsure responses with poor structure")
                st.markdown("**Strengths:** Shows engagement and willingness to respond")
                st.markdown("**Improvements:** Practice structuring responses with clear points, ask clarifying questions when needed")
                st.markdown("**Example Response:** I'm not entirely sure about this, but here's what I understand: [provide structured explanation]")
        
        # Chatty persona guidance
        if "Chatty" in personas:
            with st.expander("💬 Chatty Persona Guidance"):
                st.markdown("**Characteristics:** Goes off-topic, changes the subject, redirects conversation, or repeats questions")
                st.markdown("**Strengths:** Enthusiastic and shows good communication skills")
                st.markdown("**Improvements:** Focus on key points first, save stories for later networking")
                st.markdown("**Example Response:** The main point is X. To illustrate, [brief relevant example]. This approach has several benefits: 1) A, 2) B, 3) C.")
        
        # Edge Case persona guidance
        if "Edge Case" in personas:
            with st.expander("⚠️ Edge Case Persona Guidance"):
                st.markdown("**Characteristics:** Invalid input, audio unclear/missing, empty answer, or says 'I don't know'")
                st.markdown("**Strengths:** Direct and to the point, shows honesty")
                st.markdown("**Improvements:** Provide at least one specific detail or example to demonstrate knowledge, or briefly mention related concepts")
                st.markdown("**Example Response:** I'm not familiar with this specific concept, but I know it relates to X and Y. To learn more, I would research A, B, and C resources.")
    
    @staticmethod
    def _generate_detailed_feedback(answered_questions: List[Dict[str, Any]]):
        """Generate detailed feedback for each question."""
        if not answered_questions:
            st.info("No answered questions to provide detailed feedback for.")
            return
        
        for i, entry in enumerate(answered_questions, 1):
            question = entry.get("question", "Unknown question")
            answer = entry.get("answer", "No answer provided")
            evaluation = entry.get("evaluation", {})
            
            with st.expander(f"**Question {i}:** {question}", expanded=i==1):
                # Display answer
                st.markdown("**Your Answer:**")
                st.info(answer)
                
                # Display AI evaluation if available
                if evaluation:
                    st.markdown("**AI Evaluation & Feedback:**")
                    
                    # Overall score
                    if "overall_score" in evaluation:
                        st.metric("Score", f"{evaluation['overall_score']}/10")
                    
                    # NEW: Display communication skills if available
                    if "communication_skills" in evaluation:
                        st.metric("Communication Skills", f"{evaluation['communication_skills']}/10")
                    
                    # NEW: Display communication clarity if available
                    if "communication_clarity" in evaluation:
                        st.metric("Communication Clarity", f"{evaluation['communication_clarity']}/10")
                    
                    # Strengths
                    if "strengths" in evaluation and evaluation["strengths"]:
                        st.markdown("**Strengths:**")
                        for strength in evaluation["strengths"]:
                            st.write(f"✅ {strength}")
                    
                    # Areas for improvement
                    if "improvements" in evaluation and evaluation["improvements"]:
                        st.markdown("**Areas for Improvement:**")
                        for improvement in evaluation["improvements"]:
                            st.write(f"💡 {improvement}")
                    
                    # Perfect answer
                    if "perfect_answer" in evaluation and evaluation["perfect_answer"]:
                        st.markdown("**What a Strong Answer Would Include:**")
                        st.success(evaluation["perfect_answer"])
                    
                    # Persona
                    if "persona" in evaluation:
                        st.markdown("**Communication Style:**")
                        st.info(evaluation["persona"])
                        
                        # Special handling for specific scenarios
                        persona = evaluation["persona"]
                        if persona == "Chatty":
                            st.warning("💡 **Note:** Simply repeating the question back to the interviewer doesn't demonstrate understanding. Focus on providing your actual answer with relevant details.")
                        elif persona == "Confused":
                            st.info("💡 **Tip:** When unsure, it's okay to ask for clarification or briefly mention related concepts while showing how you'd find the answer.")
                        elif persona == "Edge Case":
                            st.warning("💡 **Note:** Brief responses can be effective, but make sure they're relevant to the question and demonstrate your knowledge.")
                else:
                    st.info("AI evaluation not available for this response.")
    
    @staticmethod
    def _generate_performance_trends(answered_questions: List[Dict[str, Any]]):
        """Generate performance trends and improvement suggestions."""
        if not answered_questions or len(answered_questions) < 2:
            st.info("Performance trends will be available after answering more questions.")
            return
        
        # Collect scores over time
        scores = []
        technical_scores = []
        behavioral_scores = []
        communication_scores = []  # NEW: Track communication skills
        
        for entry in answered_questions:
            evaluation = entry.get("evaluation", {})
            if evaluation and "overall_score" in evaluation:
                scores.append(evaluation["overall_score"])
                
                # Collect domain-specific scores
                if "technical_accuracy" in evaluation:
                    technical_scores.append(evaluation["technical_accuracy"])
                if "communication_skills" in evaluation:  # This was already here
                    communication_scores.append(evaluation["communication_skills"])
                if "teamwork_collaboration" in evaluation:  # For behavioral interviews
                    behavioral_scores.append(evaluation["teamwork_collaboration"])
        
        # Performance trend chart
        if scores:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(1, len(scores) + 1)),
                y=scores,
                mode='lines+markers',
                name='Overall Score',
                line=dict(color='blue')
            ))
            
            if technical_scores:
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(technical_scores) + 1)),
                    y=technical_scores,
                    mode='lines+markers',
                    name='Technical Score',
                    line=dict(color='green')
                ))
            
            if communication_scores:  # NEW: Add communication skills to chart
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(communication_scores) + 1)),
                    y=communication_scores,
                    mode='lines+markers',
                    name='Communication Skills',
                    line=dict(color='purple')
                ))
            
            if behavioral_scores:
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(behavioral_scores) + 1)),
                    y=behavioral_scores,
                    mode='lines+markers',
                    name='Behavioral Score',
                    line=dict(color='orange')
                ))
            
            fig.update_layout(
                title="Performance Trend Over Time",
                xaxis_title="Question Number",
                yaxis_title="Score (0-10)",
                yaxis_range=[0, 10]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Improvement suggestions
        if scores:
            st.markdown("**Improvement Suggestions:**")
            
            # Check for improvement trend
            if len(scores) >= 3:
                recent_avg = sum(scores[-3:]) / 3
                earlier_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]
                
                if recent_avg > earlier_avg:
                    st.success("✅ Your performance is improving! Keep up the good work.")
                elif recent_avg < earlier_avg:
                    st.warning("⚠️ Your performance has dipped recently. Focus on the feedback provided.")
                else:
                    st.info("🔹 Your performance is consistent. Continue practicing to improve further.")
            
            # General suggestions based on average score
            avg_score = sum(scores) / len(scores)
            if avg_score < 4:
                suggestions = [
                    "Focus on providing more structured responses using frameworks like STAR for behavioral questions",
                    "Practice answering questions with specific examples and measurable outcomes",
                    "Work on clearly addressing the question being asked rather than providing generic responses"
                ]
            elif avg_score < 7:
                suggestions = [
                    "Enhance your answers with more specific details and concrete examples",
                    "Practice explaining your thought process and decision-making approach",
                    "Focus on demonstrating both technical knowledge and soft skills in your responses"
                ]
            else:
                suggestions = [
                    "Continue practicing to maintain your high performance level",
                    "Challenge yourself with more difficult questions to further improve",
                    "Focus on refining your communication to make even strong answers more impactful"
                ]
            
            for suggestion in suggestions:
                st.write(f"💡 {suggestion}")