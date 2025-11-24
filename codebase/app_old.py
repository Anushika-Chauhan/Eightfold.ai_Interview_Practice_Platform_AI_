import json
import os
from pathlib import Path
from typing import Any, Dict, List
import streamlit as st

# Voice/AI dependencies
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    import av
    import numpy as np
    HAS_WEBRTC = True
except Exception:
    HAS_WEBRTC = False

try:
    import speech_recognition as sr
    HAS_SR = True
except Exception:
    HAS_SR = False

APP_TITLE = "AI Interview Practice Partner"
QUESTIONS_PATH = Path(__file__).parent / "questions.json"

# 7 Professional Roles
ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Frontend Engineer",
    "DevOps Engineer",
    "Product Manager",
    "UX Designer",
    "Data Analyst",
]

INTERVIEW_TYPES = ["Technical Round (45 min)", "HR & Behavioral Round (30 min)"]
PERSONAS = ["Confused", "Efficient", "Chatty", "Edge-Case"]

# =============== GEMINI AI ENGINE ===============

class GeminiAI:
    def __init__(self):
        self.key = os.environ.get("GEMINI_API_KEY")
        try:
            if not self.key:
                self.key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass
        
        self.is_ready = False
        if self.key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.is_ready = True
            except Exception as e:
                st.error(f"Gemini init failed: {e}")
    
    def evaluate_technical(self, role: str, question: str, answer: str) -> Dict[str, Any]:
        if not self.is_ready:
            return self._fallback_eval(answer)
        
        prompt = f"""You are an expert technical interviewer for {role} position.

Question: {question}
Candidate's Answer: {answer}

Evaluate and return ONLY valid JSON with:
{{
  "technical_accuracy": 0-10,
  "problem_solving": 0-10,
  "depth_of_knowledge": 0-10,
  "communication_clarity": 0-10,
  "overall_score": 0-10,
  "strengths": ["strength1", "strength2"],
  "improvements": ["area1", "area2"],
  "persona": "Confused/Efficient/Chatty/Edge-Case",
  "follow_up": "one specific follow-up question"
}}

No markdown, just JSON."""
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n```", 1)[0].strip()
            if content.startswith("json"):
                content = content[4:].strip()
            return json.loads(content)
        except Exception as e:
            st.warning(f"AI eval failed: {e}")
            return self._fallback_eval(answer)
    
    def evaluate_behavioral(self, role: str, question: str, answer: str) -> Dict[str, Any]:
        if not self.is_ready:
            return self._fallback_eval(answer)
        
        prompt = f"""You are an expert HR interviewer for {role} position.

Question: {question}
Candidate's Answer: {answer}

Evaluate and return ONLY valid JSON with:
{{
  "communication_skills": 0-10,
  "teamwork_collaboration": 0-10,
  "leadership_potential": 0-10,
  "cultural_fit": 0-10,
  "overall_score": 0-10,
  "strengths": ["strength1", "strength2"],
  "improvements": ["area1", "area2"],
  "persona": "Confused/Efficient/Chatty/Edge-Case",
  "follow_up": "one STAR-method follow-up question"
}}

No markdown, just JSON."""
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n```", 1)[0].strip()
            if content.startswith("json"):
                content = content[4:].strip()
            return json.loads(content)
        except Exception:
            return self._fallback_eval(answer)
    
    def _fallback_eval(self, answer: str) -> Dict[str, Any]:
        length = len((answer or "").split())
        score = min(10, max(1, int(length / 15)))
        return {
            "technical_accuracy": score,
            "problem_solving": score,
            "depth_of_knowledge": score,
            "communication_clarity": score,
            "overall_score": score,
            "strengths": ["Provided a response"],
            "improvements": ["Add more technical details", "Use STAR method"],
            "persona": "Efficient" if length > 30 else "Confused",
            "follow_up": "Can you elaborate with an example?"
        }

# =============== VOICE RECORDING ===============

def record_voice_answer() -> str:
    st.markdown("### 🎤 Voice Recording")
    
    if "recorded_text" not in st.session_state:
        st.session_state.recorded_text = ""
    
    # Primary: Microphone recording
    if HAS_SR:
        st.info("🎙️ Click to record your answer (speak for up to 30 seconds)")
        
        if st.button("🔴 Start Recording", type="primary", use_container_width=True):
            with st.spinner("🎤 Listening... Speak now!"):
                try:
                    recognizer = sr.Recognizer()
                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=30)
                    
                    with st.spinner("🤖 Transcribing..."):
                        text = recognizer.recognize_google(audio)
                        st.session_state.recorded_text = text
                        st.success(f"✅ Transcribed: {text}")
                        return text
                except sr.WaitTimeoutError:
                    st.error("⏱️ No speech detected. Please try again.")
                except sr.UnknownValueError:
                    st.error("🔇 Could not understand audio. Please speak clearly.")
                except sr.RequestError as e:
                    st.error(f"⚠️ Service error: {e}")
                except Exception as e:
                    st.error(f"❌ Recording failed: {e}")
        
        # Show last recorded text
        if st.session_state.recorded_text:
            st.text_area("Your answer:", st.session_state.recorded_text, height=100, disabled=True)
            return st.session_state.recorded_text
    
    # Fallback
    else:
        st.warning("⚠️ Microphone not available. Install: pip install SpeechRecognition pyaudio")
        return st.text_area("Type your answer:", height=100)

# =============== QUESTION BANK ===============

def load_questions() -> Dict[str, Dict[str, List[str]]]:
    if not QUESTIONS_PATH.exists():
        return {}
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# =============== SESSION STATE ===============

def init_state():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.stage = "setup"  # setup, interview, feedback
        st.session_state.role = ROLES[0]
        st.session_state.interview_type = INTERVIEW_TYPES[0]
        st.session_state.persona = "Efficient"
        st.session_state.q_idx = 0
        st.session_state.history = []
        st.session_state.current_answer = ""

# =============== UI PANELS ===============

def setup_panel():
    st.title(APP_TITLE)
    st.caption("🎯 Voice-Based Mock Interview Platform for Eightfold.ai Assignment")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.role = st.selectbox("🎯 Target Role", ROLES, index=ROLES.index(st.session_state.role))
        st.session_state.interview_type = st.selectbox("📋 Interview Type", INTERVIEW_TYPES, index=INTERVIEW_TYPES.index(st.session_state.interview_type))
    
    with col2:
        st.session_state.persona = st.selectbox("👤 Your Test Persona", PERSONAS, index=PERSONAS.index(st.session_state.persona))
        st.info(f"**Selected:** {st.session_state.role}\n\n**Type:** {st.session_state.interview_type}")
    
    st.markdown("---")
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        st.session_state.stage = "interview"
        st.session_state.q_idx = 0
        st.session_state.history = []
        st.rerun()

def interview_panel(ai: GeminiAI, questions: Dict[str, Dict[str, List[str]]]):
    role = st.session_state.role
    is_technical = "Technical" in st.session_state.interview_type
    round_type = "Technical" if is_technical else "Behavioral"
    
    qs = questions.get(role, {}).get(round_type, [])
    if not qs:
        st.error(f"No questions found for {role} - {round_type}")
        return
    
    if st.session_state.q_idx >= len(qs):
        st.session_state.stage = "feedback"
        st.rerun()
        return
    
    question = qs[st.session_state.q_idx]
    
    st.title(f"{round_type} Interview: {role}")
    st.caption(f"Question {st.session_state.q_idx + 1} of {len(qs)}")
    st.markdown("---")
    
    st.subheader("📝 Question")
    st.write(question)
    st.markdown("---")
    
    answer = record_voice_answer()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏭️ Skip Question"):
            st.session_state.history.append({
                "question": question,
                "answer": "",
                "skipped": True,
                "evaluation": {}
            })
            st.session_state.q_idx += 1
            st.rerun()
    
    with col2:
        if answer and answer.strip():
            if st.button("✅ Submit Answer", type="primary"):
                with st.spinner("🤖 AI is evaluating..."):
                    if is_technical:
                        evaluation = ai.evaluate_technical(role, question, answer)
                    else:
                        evaluation = ai.evaluate_behavioral(role, question, answer)
                
                st.session_state.history.append({
                    "question": question,
                    "answer": answer,
                    "skipped": False,
                    "evaluation": evaluation
                })
                
                # Show instant feedback
                st.success("✅ Answer submitted!")
                st.markdown("### 🎯 Instant Feedback")
                st.json(evaluation)
                
                if st.button("➡️ Next Question"):
                    st.session_state.q_idx += 1
                    st.rerun()
    
    with col3:
        if st.button("🛑 End Interview"):
            st.session_state.stage = "feedback"
            st.rerun()

def feedback_panel():
    st.title("📊 Final Interview Report")
    st.markdown("---")
    
    history = st.session_state.history
    if not history:
        st.warning("No answers recorded.")
        if st.button("🔄 Restart"):
            st.session_state.stage = "setup"
            st.rerun()
        return
    
    # Calculate overall scores
    evals = [h["evaluation"] for h in history if not h.get("skipped") and h.get("evaluation")]
    if evals:
        avg_score = sum(e.get("overall_score", 0) for e in evals) / len(evals)
        st.metric("Overall Performance", f"{avg_score:.1f}/10", f"{len(evals)} questions answered")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Strengths")
            all_strengths = []
            for e in evals:
                all_strengths.extend(e.get("strengths", []))
            for s in sorted(set(all_strengths))[:5]:
                st.write(f"• {s}")
        
        with col2:
            st.subheader("🔧 Areas for Improvement")
            all_improvements = []
            for e in evals:
                all_improvements.extend(e.get("improvements", []))
            for i in sorted(set(all_improvements))[:5]:
                st.write(f"• {i}")
        
        st.markdown("---")
        st.subheader("📝 Detailed Q&A Review")
        for idx, h in enumerate(history, 1):
            with st.expander(f"Question {idx}: {h['question'][:60]}..."):
                st.write(f"**Q:** {h['question']}")
                if h.get("skipped"):
                    st.write("**A:** (Skipped)")
                else:
                    st.write(f"**A:** {h['answer']}")
                    if h.get("evaluation"):
                        st.json(h["evaluation"])
    
    st.markdown("---")
    if st.button("🔄 Start New Interview", type="primary"):
        st.session_state.stage = "setup"
        st.session_state.q_idx = 0
        st.session_state.history = []
        st.rerun()

# =============== MAIN APP ===============

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🎤", layout="wide")
    init_state()
    
    ai = GeminiAI()
    questions = load_questions()
    
    if st.session_state.stage == "setup":
        setup_panel()
    elif st.session_state.stage == "interview":
        interview_panel(ai, questions)
    elif st.session_state.stage == "feedback":
        feedback_panel()

if __name__ == "__main__":
    main()
