"""
AI Interview Practice Partner
Eightfold.ai Assignment Submission

Main Streamlit application for voice-based mock interviews.
"""

import streamlit as st
from config import ROLES, INTERVIEW_TYPES
from utils import AIEvaluator, record_voice_answer, ConversationManager, FeedbackGenerator

# Text-to-speech imports
try:
    import pyttsx3
    HAS_TTS = True
except Exception:
    HAS_TTS = False

APP_TITLE = "AI Interview Practice Partner"
APP_SUBTITLE = "Voice-Based Mock Interview Platform"


def greeting_panel():
    """Initial greeting and introduction panel."""
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    
    # Check AI status
    ai = AIEvaluator()
    if ai.is_ready:
        st.success("AI is ready for evaluation")
    else:
        st.error("AI not available - using fallback evaluation")
        st.warning("Please check your API configuration")
    
    st.markdown("---")
    
    # Greeting message
    greeting = "Welcome to your AI interview practice session! I'm your virtual interview coach, and I'm here to help you prepare for your upcoming interview. Let's get started by understanding what role you're preparing for and what type of interview you'd like to practice."
    st.info(greeting)
    
    # Text-to-speech for greeting
    if HAS_TTS and not st.session_state.greeting_complete:
        try:
            engine = pyttsx3.init()
            # Adjust speech rate and volume for better clarity
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            engine.say(greeting)
            engine.runAndWait()
            st.session_state.greeting_complete = True
        except Exception as e:
            pass
    
    st.markdown("---")
    
    st.info("When you're ready, just say 'start' or click the button below to begin.")
    
    # Voice command to start
    st.markdown("### Voice Command")
    st.info("Click the button below and say 'start' to begin")
    
    if st.button("🎙 Say 'Start'", type="primary", use_container_width=True):
        with st.spinner("Listening for voice command..."):
            try:
                import speech_recognition as sr
                # Create recognizer
                recognizer = sr.Recognizer()
                
                # Configure for human speech
                recognizer.pause_threshold = 1.0
                recognizer.non_speaking_duration = 0.5
                recognizer.dynamic_energy_threshold = False
                recognizer.energy_threshold = 400
                
                # Record from microphone
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    # Listen for up to 5 seconds
                    audio = recognizer.listen(source, phrase_time_limit=5)
                
                # Transcribe
                with st.spinner("Processing your command..."):
                    text = recognizer.recognize_google(audio).lower()
                    
                    # Check if user said "start" or similar command
                    start_commands = ["start", "begin", "let's go", "lets go", "yes", "okay", "sure"]
                    
                    if any(command in text for command in start_commands):
                        st.session_state.stage = "role_selection"
                        st.rerun()
                    else:
                        st.error("I didn't catch that. Please say 'start' or click the button again.")
                        
            except sr.WaitTimeoutError:
                st.error("No speech detected. Click the button again and say 'start'.")
            except sr.UnknownValueError:
                st.error("Could not understand audio. Please say 'start' clearly.")
            except sr.RequestError as e:
                st.error(f"Service error: {e}")
            except Exception as e:
                st.error(f"Error processing command: {e}")
    
    # Alternative: Direct button
    if st.button("Continue", use_container_width=True):
        st.session_state.stage = "role_selection"
        st.rerun()

def role_selection_panel():
    """Panel for selecting role via voice input."""
    st.title("Role Selection")
    st.caption("Please tell me which role you want to prepare for")
    
    # Role selection prompt
    role_prompt = "What role are you preparing for? Please tell me the job title you're interested in, such as software engineer, data scientist, product manager, or any other role you'd like to practice for. I'm listening for your response now."
    st.info(role_prompt)
    
    # Text-to-speech for role prompt
    if HAS_TTS and not st.session_state.role_selected:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say(role_prompt)
            engine.runAndWait()
        except Exception as e:
            pass
    
    st.markdown("---")
    
    # Automatically start voice recording for role selection
    st.markdown("### Listening for your response...")
    st.info("🎤 I'm listening for your role selection. Please speak clearly now.")
    
    # Auto-start recording
    with st.spinner("🔴 Listening... Please speak clearly!"):
        try:
            import speech_recognition as sr
            # Create recognizer
            recognizer = sr.Recognizer()
            
            # Configure for human speech
            recognizer.pause_threshold = 1.0
            recognizer.non_speaking_duration = 0.5
            recognizer.dynamic_energy_threshold = False
            recognizer.energy_threshold = 400
            
            # Record from microphone
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                # Listen for up to 15 seconds
                audio = recognizer.listen(source, phrase_time_limit=15)
            
            # Transcribe
            with st.spinner("Converting speech to text..."):
                text = recognizer.recognize_google(audio)
                
                # Use AI to extract role from user's response
                ai = AIEvaluator()
                if ai.is_ready:
                    # Generate prompt for AI to extract role
                    prompt = f"""Extract the job role from the following user response. 
                    The user is saying what job role they want to prepare for an interview. 
                    Extract just the job title from their response.
                    User response: {text}
                    
                    Return ONLY the job title, nothing else."""
                    
                    try:
                        import google.generativeai as genai
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        response = model.generate_content(prompt)
                        extracted_role = response.text.strip()
                        
                        if extracted_role:
                            st.session_state.role = extracted_role
                            st.session_state.role_selected = True
                            st.success(f"Role identified: {extracted_role}")
                            st.session_state.stage = "interview_type_selection"
                            st.rerun()
                        else:
                            st.error("Could not identify a role from your response. Please try again and clearly state the job title.")
                    except Exception as e:
                        st.error("Could not process your response. Please try again.")
                else:
                    # Fallback: use the raw text as role
                    if text and len(text.strip()) > 0:
                        st.session_state.role = text.strip()
                        st.session_state.role_selected = True
                        st.success(f"Role identified: {text.strip()}")
                        st.session_state.stage = "interview_type_selection"
                        st.rerun()
                    else:
                        st.error("Could not understand your response. Please try again and clearly state the job title.")
                    
        except sr.WaitTimeoutError:
            st.error("No speech detected. Please refresh the page and try again.")
        except sr.UnknownValueError:
            st.error("Could not understand audio. Please refresh the page and speak more clearly.")
        except sr.RequestError as e:
            st.error(f"Service error: {e}")
        except Exception as e:
            st.error(f"Recording failed: {e}")
    
    st.markdown("---")
    
    # Back button
    if st.button("⬅️ Back", use_container_width=True):
        st.session_state.stage = "greeting"
        st.rerun()

def interview_type_selection_panel():
    """Panel for selecting interview type via voice input."""
    st.title("Interview Type Selection")
    st.caption(f"Selected Role: {st.session_state.role}")
    
    # Interview type selection prompt
    type_prompt = f"What type of interview would you like to practice for the {st.session_state.role} position? You can choose technical, behavioral, or HR interview. Please tell me your preference. I'm listening for your response now."
    st.info(type_prompt)
    
    # Text-to-speech for interview type prompt
    if HAS_TTS and not st.session_state.interview_type_selected:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say(type_prompt)
            engine.runAndWait()
        except Exception as e:
            pass
    
    st.markdown("---")
    
    # Automatically start voice recording for interview type selection
    st.markdown("### Listening for your response...")
    st.info("🎤 I'm listening for your interview type selection. Please speak clearly now.")
    
    # Auto-start recording
    with st.spinner("🔴 Listening... Please speak clearly!"):
        try:
            import speech_recognition as sr
            # Create recognizer
            recognizer = sr.Recognizer()
            
            # Configure for human speech
            recognizer.pause_threshold = 1.0
            recognizer.non_speaking_duration = 0.5
            recognizer.dynamic_energy_threshold = False
            recognizer.energy_threshold = 400
            
            # Record from microphone
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                # Listen for up to 15 seconds
                audio = recognizer.listen(source, phrase_time_limit=15)
            
            # Transcribe
            with st.spinner("Converting speech to text..."):
                text = recognizer.recognize_google(audio)
                
                # Use AI to extract interview type from user's response
                ai = AIEvaluator()
                if ai.is_ready:
                    # Generate prompt for AI to extract interview type
                    prompt = f"""Extract the interview type from the following user response. 
                    The user is saying what type of interview they want to practice for the {st.session_state.role} position.
                    They might say technical, behavioral, or HR interview.
                    User response: {text}
                    
                    Return ONLY one of these three options: Technical Interview, Behavioral Interview, or HR Interview.
                    If you cannot determine the type, return Behavioral Interview as default."""
                    
                    try:
                        import google.generativeai as genai
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        response = model.generate_content(prompt)
                        extracted_type = response.text.strip()
                        
                        # Validate the extracted type
                        valid_types = ["Technical Interview", "Behavioral Interview", "HR Interview"]
                        selected_type = None
                        for valid_type in valid_types:
                            if valid_type.lower() in extracted_type.lower():
                                selected_type = valid_type
                                break
                        
                        # Default to Behavioral if not found
                        if not selected_type:
                            selected_type = "Behavioral Interview"
                        
                        st.session_state.interview_type = selected_type
                        st.session_state.interview_type_selected = True
                        st.success(f"Interview type identified: {selected_type}")
                        st.session_state.stage = "instructions"
                        st.session_state.history = []
                        st.rerun()
                    except Exception as e:
                        # Fallback to default
                        st.session_state.interview_type = "Behavioral Interview"
                        st.session_state.interview_type_selected = True
                        st.success("Interview type set to: Behavioral Interview")
                        st.session_state.stage = "instructions"
                        st.session_state.history = []
                        st.rerun()
                else:
                    # Fallback: try to extract from text
                    text_lower = text.lower()
                    if "technical" in text_lower:
                        selected_type = "Technical Interview"
                    elif "hr" in text_lower:
                        selected_type = "HR Interview"
                    else:
                        selected_type = "Behavioral Interview"  # default
                    
                    st.session_state.interview_type = selected_type
                    st.session_state.interview_type_selected = True
                    st.success(f"Interview type identified: {selected_type}")
                    st.session_state.stage = "instructions"
                    st.session_state.history = []
                    st.rerun()
                    
        except sr.WaitTimeoutError:
            st.error("No speech detected. Please refresh the page and try again.")
        except sr.UnknownValueError:
            st.error("Could not understand audio. Please refresh the page and speak more clearly.")
        except sr.RequestError as e:
            st.error(f"Service error: {e}")
        except Exception as e:
            st.error(f"Recording failed: {e}")
    
    st.markdown("---")
    
    # Back button
    if st.button("⬅️ Back", use_container_width=True):
        st.session_state.stage = "role_selection"
        st.rerun()

def setup_panel():
    """Setup screen for interview configuration."""
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    
    # Check AI status
    ai = AIEvaluator()
    if ai.is_ready:
        st.success("AI is ready for evaluation")
    else:
        st.error("AI not available - using fallback evaluation")
        st.warning("Please check your API configuration")
    
    st.markdown("---")
    
    # Role and interview type selection
    role = st.selectbox("Target Role", ROLES, index=0)
    interview_type = st.selectbox("Interview Type", INTERVIEW_TYPES, index=0)
    
    st.info(f"**Selected Configuration:** Role: {role} | Type: {interview_type}")
    
    st.markdown("---")
    
    if st.button("Start Interview", type="primary", use_container_width=True):
        st.session_state.role = role
        st.session_state.interview_type = interview_type
        st.session_state.stage = "instructions"  # Go to instructions first
        st.session_state.history = []
        st.rerun()


def instructions_panel():
    """Instructions screen before starting the interview."""
    st.title("Interview Instructions")
    st.caption(f"Role: {st.session_state.role} | Type: {st.session_state.interview_type}")
    
    # AI greeting
    greeting = f"Great! I'll be your interviewer for the {st.session_state.role} position today. I'll ask you a series of questions and you'll have up to 3 minutes to answer each one. Don't worry if you don't know an answer - just say so honestly. Let's begin when you're ready!"
    st.info(greeting)
    
    # Text-to-speech for greeting
    if HAS_TTS and not st.session_state.get("instructions_spoken", False):
        try:
            engine = pyttsx3.init()
            # Adjust speech rate and volume for better clarity
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            engine.say(greeting)
            engine.runAndWait()
            st.session_state.instructions_spoken = True
        except Exception as e:
            pass
    
    # Instructions
    st.subheader("🎤 Interview Instructions")
    instructions = [
        "The AI will speak each question aloud",
        "You'll have up to 3 minutes to answer each question",
        "Speak clearly into your microphone when answering",
        "If you don't know an answer, just say 'I don't know' honestly",
        "After each answer, I'll ask if you want to move to the next question",
        "Complete all 6 questions for a full evaluation"
    ]
    
    for i, instruction in enumerate(instructions, 1):
        st.write(f"{i}. {instruction}")
    
    st.markdown("---")
    
    # Automatically ask to start after instructions
    start_prompt = "Are you ready to begin the interview? Please say 'yes' to start or 'no' if you need more time."
    st.info(start_prompt)
    
    # Text-to-speech for start prompt
    if HAS_TTS and st.session_state.get("instructions_spoken", False):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say(start_prompt)
            engine.runAndWait()
        except Exception as e:
            pass
    
    # Automatically start listening for response
    st.markdown("### Listening for your response...")
    st.info("🎤 I'm listening for your response. Please say 'yes' to start or 'no' if you need more time.")
    
    # Auto-start recording for start confirmation
    with st.spinner("Listening for your response..."):
        try:
            import speech_recognition as sr
            # Create recognizer
            recognizer = sr.Recognizer()
            
            # Configure for human speech
            recognizer.pause_threshold = 1.0
            recognizer.non_speaking_duration = 0.5
            recognizer.dynamic_energy_threshold = False
            recognizer.energy_threshold = 400
            
            # Record from microphone
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                # Listen for up to 5 seconds
                audio = recognizer.listen(source, phrase_time_limit=5)
            
            # Transcribe
            with st.spinner("Processing your response..."):
                text = recognizer.recognize_google(audio).lower()
                
                # Check if user said "yes" or similar command
                yes_commands = ["yes", "yeah", "yep", "sure", "okay", "start", "begin", "lets go", "let's go"]
                no_commands = ["no", "nope", "not yet", "wait"]
                
                if any(command in text for command in yes_commands):
                    st.session_state.stage = "generating_questions"
                    st.session_state.instructions_spoken = False
                    st.rerun()
                elif any(command in text for command in no_commands):
                    st.info("Okay, take your time. When you're ready, please refresh the page to continue.")
                else:
                    st.error("I didn't catch that. Please refresh the page and say 'yes' to start or 'no' if you need more time.")
                    
        except sr.WaitTimeoutError:
            st.error("No speech detected. Please refresh the page and try again.")
        except sr.UnknownValueError:
            st.error("Could not understand audio. Please refresh the page and speak clearly.")
        except sr.RequestError as e:
            st.error(f"Service error: {e}")
        except Exception as e:
            st.error(f"Error processing response: {e}")
    
    # Back button
    if st.button("⬅️ Back", use_container_width=True):
        st.session_state.stage = "interview_type_selection"
        st.session_state.instructions_spoken = False
        st.rerun()

def generating_questions_panel():
    """Panel for generating all questions at once."""
    st.title("Preparing Your Interview")
    st.info(f"Generating 6 questions for {st.session_state.role} - {st.session_state.interview_type}...")
    
    # Show progress
    st.markdown("---")
    st.markdown("### Generating Interview Questions")
    
    # Initialize AI evaluator
    ai = AIEvaluator()
    
    # Determine round type
    is_technical = "Technical" in st.session_state.interview_type
    round_type = "Technical" if is_technical else "Behavioral"
    
    # Check if questions were already generated
    if "questions" not in st.session_state or not st.session_state.questions:
        # Generate all 6 questions at once
        with st.spinner("AI is creating your personalized questions..."):
            st.session_state.questions = []
            question_history = []
            
            # Generate 6 unique questions
            for i in range(6):
                question = ai.generate_question(st.session_state.role, round_type, question_history)
                st.session_state.questions.append(question)
                question_history.append(question)
            
            # Reset question index tracking
            st.session_state.current_question_idx = 0
    
    # Move to interview stage
    st.session_state.stage = "interview"
    st.rerun()


def interview_panel():
    """Main interview interface."""
    role = st.session_state.role
    interview_type = st.session_state.interview_type
    is_technical = "Technical" in interview_type
    round_type = "Technical" if is_technical else "Behavioral"
    
    # Initialize AI evaluator
    ai = AIEvaluator()
    
    # Check if questions were generated
    if "questions" not in st.session_state or not st.session_state.questions:
        st.error("No questions available. Please restart the interview.")
        if st.button("Restart Interview"):
            st.session_state.stage = "setup"
            st.rerun()
        return
    
    # Limit to 6 questions
    if st.session_state.current_question_idx >= 6:
        # Evaluate all answers at the end
        with st.spinner("AI is evaluating all your responses..."):
            for item in st.session_state.history:
                if not item.get("skipped") and not item.get("evaluation"):
                    # Check if this was a "don't know" response
                    if item.get("dont_know", False):
                        # Create a special evaluation for "don't know" responses
                        evaluation = {
                            "overall_score": 0,
                            "strengths": ["Honesty in acknowledging knowledge gaps"],
                            "improvements": ["Try to provide partial knowledge or related experience even when unsure"],
                            "persona": "Edge Case",
                            "follow_up": "Can you tell me about a time you encountered a knowledge gap and how you addressed it?",
                            "perfect_answer": "When you're unsure about something, it's better to acknowledge it honestly but also mention related knowledge or how you would find the answer."
                        }
                        
                        # Add technical or behavioral specific fields
                        if is_technical:
                            evaluation.update({
                                "technical_accuracy": 0,
                                "problem_solving": 0,
                                "depth_of_knowledge": 0,
                                "communication_clarity": 5  # Give some credit for clear communication
                            })
                        else:
                            evaluation.update({
                                "communication_skills": 5,  # Give some credit for clear communication
                                "teamwork_collaboration": 0,
                                "leadership_potential": 0,
                                "cultural_fit": 0
                            })
                    else:
                        # Normal evaluation with persona history
                        persona_history = [h["evaluation"]["persona"] for h in st.session_state.history 
                                         if h.get("evaluation") and h["evaluation"].get("persona")]
                        
                        if is_technical:
                            evaluation = ai.evaluate_technical(role, item["question"], item["answer"], persona_history)
                        else:
                            evaluation = ai.evaluate_behavioral(role, item["question"], item["answer"], persona_history)
                    item["evaluation"] = evaluation
        
        st.session_state.stage = "feedback"
        st.rerun()
        return
    
    # Get current question
    question = st.session_state.questions[st.session_state.current_question_idx]
    
    # Header
    st.title(f"{round_type} Interview: {role}")
    st.caption(f"Question {st.session_state.current_question_idx + 1} of 6")
    
    # Progress bar
    progress = (st.session_state.current_question_idx + 1) / 6
    st.progress(progress)
    
    st.markdown("---")
    
    # Question display
    st.subheader("Question")
    st.write(question)
    
    # Automatically speak the question when it appears (only once)
    # Only speak question after greeting is complete
    if HAS_TTS and not st.session_state.get(f"question_{st.session_state.current_question_idx}_spoken", False):
        try:
            engine = pyttsx3.init()
            # Adjust speech rate and volume for better clarity
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            # For first question, wait for greeting to complete
            if st.session_state.current_question_idx == 0:
                # Wait until greeting is complete
                max_wait = 5  # Maximum wait time in seconds
                waited = 0
                while not st.session_state.get("greeting_complete", False) and waited < max_wait:
                    import time
                    time.sleep(0.1)
                    waited += 0.1
                
                # Add extra pause after greeting
                import time
                time.sleep(1.0)
            
            engine.say(f"Here's your question: {question}")
            engine.runAndWait()
            st.session_state[f"question_{st.session_state.current_question_idx}_spoken"] = True
        except Exception as e:
            pass  # Fail silently if TTS fails
    
    # Clean up greeting flag after first question
    if st.session_state.current_question_idx > 0 and "greeting_complete" in st.session_state:
        del st.session_state["greeting_complete"]
    
    st.markdown("---")
    
    # Voice recording with improved handling
    answer = record_voice_answer(reset_state=False)
    
    # Display recorded answer if available
    if st.session_state.voice_recording_complete and st.session_state.voice_answer:
        st.markdown("### Your Answer")
        st.info(st.session_state.voice_answer)
        
        # Check if user said "I don't know" or similar
        answer_text = st.session_state.voice_answer.lower()
        dont_know_phrases = ["i don't know", "i dont know", "don't know", "dont know", "i'm not sure", "im not sure", "not sure"]
        is_dont_know = any(phrase in answer_text for phrase in dont_know_phrases)
        
        # Handle "I don't know" responses with brief, encouraging feedback
        if is_dont_know:
            st.markdown("### AI Response")
            # Use AI to provide a brief, encouraging explanation
            if ai.is_ready:
                try:
                    import google.generativeai as genai
                    # Generate a brief, helpful response
                    help_prompt = f"""You are a supportive interview coach. The candidate said they don't know the answer to this question: '{question}'. 
                    Provide a very brief, encouraging response (4-5 lines) that:
                    1. Acknowledges it's okay not to know everything
                    2. Briefly explains what a good answer might include with technical details
                    3. Encourages them positively
                    4. Suggests how they could approach learning this topic
                    
                    Keep it comprehensive but friendly."""
                    
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    response = model.generate_content(help_prompt)
                    helpful_response = response.text.strip()
                except Exception as e:
                    helpful_response = "That's okay! A good answer would cover the key concepts with specific examples. To learn this topic, I'd recommend researching industry best practices and practicing with real-world scenarios. Let's move to the next question."
            else:
                helpful_response = "That's okay! A good answer would cover the key concepts with specific examples. To learn this topic, I'd recommend researching industry best practices and practicing with real-world scenarios. Let's move to the next question."
            
            st.info(helpful_response)
            
            # Text-to-speech for response
            if HAS_TTS:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 150)
                    engine.setProperty('volume', 0.9)
                    engine.say(helpful_response)
                    engine.runAndWait()
                except Exception as e:
                    pass
            
            # Save answer and move to next question
            st.session_state.history.append({
                "question": question,
                "answer": st.session_state.voice_answer,
                "timestamp": st.session_state.get("timestamp", ""),
                "skipped": False,
                "evaluation": None,
                "dont_know": True
            })
            st.session_state.current_question_idx += 1
            # Reset recording state
            keys_to_delete = [key for key in st.session_state.keys() if key.startswith("voice_")]
            for key in keys_to_delete:
                del st.session_state[key]
            st.rerun()
        else:
            # Ask AI to evaluate the answer and decide next step with a more relaxed approach
            if ai.is_ready:
                # Generate prompt for AI to evaluate answer and decide next step
                evaluation_prompt = f"""You are a supportive interview coach. The candidate just answered the question: '{question}'
                Their answer was: '{st.session_state.voice_answer}'
                
                First, provide a comprehensive evaluation of their answer (4-5 lines). Start with something positive they did well.
                Then, politely mention 2-3 areas where they could improve (be constructive, not critical).
                Finally, determine if their answer shows sufficient understanding to move on, or if they need clarification.
                Only ask a follow-up question if their answer is mostly correct but needs expansion or clarification.
                If their answer is incorrect or incomplete, provide brief, gentle feedback and suggest moving on.
                
                Special handling for specific scenarios:
                - If the user repeats the question back to the AI, this is a Chatty persona behavior. Politely tell them that simply repeating the question doesn't demonstrate understanding and encourage them to provide their actual answer.
                - If the user gives vague or incomplete answers, this is a Confused persona. Offer scaffolding to help them structure their response.
                - If the user gives minimal but correct responses, this is an Efficient persona. Acknowledge their conciseness while ensuring they've covered key points.
                - If the user gives useless or completely wrong answers, this is an Edge-Case persona. Politely redirect them to provide a relevant response.
                - If the user honestly admits knowledge gaps but tries to explain related concepts, this is an Edge Case persona. Appreciate their honesty and guide them on how to approach unknown topics.
                - If the user wants to move to the next topic or discuss instead of answering, this is a Chatty persona. Politely redirect them to answer the current question.
                
                Use these STRICT persona categories:
                1. Efficient User: Short, direct answers that stay on topic with no off-topic content and directly address the question
                2. Confused User: Unclear, fragmented, contradictory, or unsure responses with poor structure
                3. Chatty User: Goes off-topic, changes the subject, redirects conversation, or repeats questions
                4. Edge Case User: Invalid input, audio unclear/missing, empty answer, or says 'I don't know'
                
                Classification Rules:
                - If they ask to repeat the question or say "can you repeat" → Chatty
                - If they change the subject or go off-topic → Chatty
                - If they express interest in discussing/going over topics rather than answering directly → Chatty
                - If they say "move to next topic" or similar phrases like "can we discuss this instead" → Chatty
                - If they directly address the question with a clear answer:
                  * If answer score is above 5 AND directly addresses question → Efficient
                  * If answer score is 5 or below OR doesn't directly address question → Confused
                - If they ask for a follow-up question or show interest in deeper discussion → Efficient
                - Saying 'I don't know' → Edge Case
                - Audio not understood/missing → Edge Case
                
                Respond in this exact format:
                EVALUATION: [Your comprehensive evaluation - 4-5 lines with positive start, then 2-3 improvement areas]
                NEXT_STEP: [Either 'MOVE_ON' or 'FOLLOW_UP' or 'GENTLE_FEEDBACK']
                FOLLOW_UP_QUESTION: [Only if NEXT_STEP is 'FOLLOW_UP', otherwise write 'None']
                GENTLE_FEEDBACK: [Only if NEXT_STEP is 'GENTLE_FEEDBACK', otherwise write 'None']"""
                
                try:
                    import google.generativeai as genai
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    response = model.generate_content(evaluation_prompt)
                    ai_response = response.text.strip()
                    
                    # Parse AI response
                    evaluation = ""
                    next_step = "MOVE_ON"
                    followup_question = "None"
                    gentle_feedback = "None"
                    
                    lines = ai_response.split('\n')
                    for line in lines:
                        if line.startswith("EVALUATION:"):
                            evaluation = line.replace("EVALUATION:", "").strip()
                        elif line.startswith("NEXT_STEP:"):
                            next_step = line.replace("NEXT_STEP:", "").strip()
                        elif line.startswith("FOLLOW_UP_QUESTION:"):
                            followup_question = line.replace("FOLLOW_UP_QUESTION:", "").strip()
                        elif line.startswith("GENTLE_FEEDBACK:"):
                            gentle_feedback = line.replace("GENTLE_FEEDBACK:", "").strip()
                    
                    # Display AI evaluation and feedback together
                    st.markdown("### AI Evaluation & Feedback")
                    st.info(evaluation)
                    
                    # Text-to-speech for evaluation
                    if HAS_TTS:
                        try:
                            engine = pyttsx3.init()
                            engine.setProperty('rate', 150)
                            engine.setProperty('volume', 0.9)
                            engine.say(evaluation)
                            engine.runAndWait()
                        except Exception as e:
                            pass
                    
                    if "FOLLOW_UP" in next_step and followup_question != "None":
                        st.markdown("### Follow-up Question")
                        followup_message = f"Since you got the core idea, here's a follow-up question for you on this topic: {followup_question}"
                        st.info(followup_message)
                        
                        # Text-to-speech for follow-up question
                        if HAS_TTS:
                            try:
                                engine = pyttsx3.init()
                                engine.setProperty('rate', 150)
                                engine.setProperty('volume', 0.9)
                                engine.say(followup_message)
                                engine.runAndWait()
                            except Exception as e:
                                pass
                        
                        # Wait 5 seconds before recording follow-up response
                        st.markdown("### Preparing to record your response...")
                        st.info("🎤 You have 5 seconds to prepare your answer. I'll let you know when to start speaking.")
                        
                        # Add 5-second delay
                        import time
                        time.sleep(5)
                        
                        # Notify user to start speaking
                        st.info("🎤 Answer now!")
                        
                        # Automatically record follow-up response
                        st.markdown("### Listening for your response...")
                        st.info("🎤 I'm listening for your response. Please speak clearly now.")
                        
                        # Auto-start recording for follow-up response
                        with st.spinner("🔴 Recording follow-up response... Speak now! (Up to 2 minutes)"):
                            try:
                                import speech_recognition as sr
                                # Create recognizer
                                recognizer = sr.Recognizer()
                                
                                # Configure for human speech
                                recognizer.pause_threshold = 1.0
                                recognizer.non_speaking_duration = 0.5
                                recognizer.dynamic_energy_threshold = False
                                recognizer.energy_threshold = 400
                                
                                # Record from microphone
                                with sr.Microphone() as source:
                                    recognizer.adjust_for_ambient_noise(source, duration=1)
                                    # Listen for up to 2 minutes
                                    audio = recognizer.listen(source, phrase_time_limit=120)
                                
                                # Transcribe
                                with st.spinner("Converting speech to text..."):
                                    followup_answer = recognizer.recognize_google(audio)
                                    
                                    # Combine original and follow-up answers
                                    combined_answer = f"Original answer: {st.session_state.voice_answer}\n\nFollow-up response: {followup_answer}"
                                    
                                    # Save combined answer and evaluate it properly
                                    # Treat follow-up as part of the same question but evaluate separately
                                    st.session_state.history.append({
                                        "question": question,
                                        "answer": st.session_state.voice_answer,
                                        "timestamp": st.session_state.get("timestamp", ""),
                                        "skipped": False,
                                        "evaluation": None,
                                        "dont_know": False,
                                        "is_follow_up": False  # Original answer
                                    })
                                    
                                    # Evaluate the original answer
                                    persona_history = [h["evaluation"]["persona"] for h in st.session_state.history 
                                                     if h.get("evaluation") and h["evaluation"].get("persona")]
                                    
                                    if is_technical:
                                        original_evaluation = ai.evaluate_technical(role, question, st.session_state.voice_answer, persona_history)
                                    else:
                                        original_evaluation = ai.evaluate_behavioral(role, question, st.session_state.voice_answer, persona_history)
                                    
                                    # Update the last history item with evaluation
                                    st.session_state.history[-1]["evaluation"] = original_evaluation
                                    
                                    # Add follow-up as a separate entry for proper evaluation
                                    st.session_state.history.append({
                                        "question": f"Follow-up: {followup_question}",
                                        "answer": followup_answer,
                                        "timestamp": st.session_state.get("timestamp", ""),
                                        "skipped": False,
                                        "evaluation": None,
                                        "dont_know": False,
                                        "is_follow_up": True,
                                        "original_question": question
                                    })
                                    
                                    # Evaluate the follow-up answer
                                    if is_technical:
                                        followup_evaluation = ai.evaluate_technical(role, followup_question, followup_answer, persona_history + [original_evaluation["persona"]] if "persona" in original_evaluation else persona_history)
                                    else:
                                        followup_evaluation = ai.evaluate_behavioral(role, followup_question, followup_answer, persona_history + [original_evaluation["persona"]] if "persona" in original_evaluation else persona_history)
                                    
                                    # Update the follow-up history item with evaluation
                                    st.session_state.history[-1]["evaluation"] = followup_evaluation
                                    
                                    st.session_state.current_question_idx += 1
                                    # Reset recording state
                                    keys_to_delete = [key for key in st.session_state.keys() if key.startswith("voice_")]
                                    for key in keys_to_delete:
                                        del st.session_state[key]
                                    st.rerun()
                            except sr.WaitTimeoutError:
                                # No follow-up response, evaluate original answer and move to next question
                                st.session_state.history.append({
                                    "question": question,
                                    "answer": st.session_state.voice_answer,
                                    "timestamp": st.session_state.get("timestamp", ""),
                                    "skipped": False,
                                    "evaluation": None,
                                    "dont_know": False,
                                    "is_follow_up": False
                                })
                                
                                # Evaluate the original answer
                                persona_history = [h["evaluation"]["persona"] for h in st.session_state.history 
                                                 if h.get("evaluation") and h["evaluation"].get("persona")]
                                
                                if is_technical:
                                    original_evaluation = ai.evaluate_technical(role, question, st.session_state.voice_answer, persona_history)
                                else:
                                    original_evaluation = ai.evaluate_behavioral(role, question, st.session_state.voice_answer, persona_history)
                                
                                # Update the last history item with evaluation
                                st.session_state.history[-1]["evaluation"] = original_evaluation
                                
                                st.session_state.current_question_idx += 1
                                # Reset recording state
                                keys_to_delete = [key for key in st.session_state.keys() if key.startswith("voice_")]
                                for key in keys_to_delete:
                                    del st.session_state[key]
                                st.rerun()
                            except Exception as e:
                                # Error in follow-up recording, evaluate original answer and move to next question
                                st.session_state.history.append({
                                    "question": question,
                                    "answer": st.session_state.voice_answer,
                                    "timestamp": st.session_state.get("timestamp", ""),
                                    "skipped": False,
                                    "evaluation": None,
                                    "dont_know": False,
                                    "is_follow_up": False
                                })
                                
                                # Evaluate the original answer
                                persona_history = [h["evaluation"]["persona"] for h in st.session_state.history 
                                                 if h.get("evaluation") and h["evaluation"].get("persona")]
                                
                                if is_technical:
                                    original_evaluation = ai.evaluate_technical(role, question, st.session_state.voice_answer, persona_history)
                                else:
                                    original_evaluation = ai.evaluate_behavioral(role, question, st.session_state.voice_answer, persona_history)
                                
                                # Update the last history item with evaluation
                                st.session_state.history[-1]["evaluation"] = original_evaluation
                                
                                st.session_state.current_question_idx += 1
                                # Reset recording state
                                keys_to_delete = [key for key in st.session_state.keys() if key.startswith("voice_")]
                                for key in keys_to_delete:
                                    del st.session_state[key]
                                st.rerun()
                    elif "GENTLE_FEEDBACK" in next_step and gentle_feedback != "None":
                        st.markdown("### AI Feedback")
                        st.info(gentle_feedback)
                        
                        # Text-to-speech for feedback
                        if HAS_TTS:
                            try:
                                engine = pyttsx3.init()
                                engine.setProperty('rate', 150)
                                engine.setProperty('volume', 0.9)
                                engine.say(gentle_feedback)
                                engine.runAndWait()
                            except Exception as e:
                                pass
                        
                        # Move to next question automatically and evaluate the answer
                        st.session_state.history.append({
                            "question": question,
                            "answer": st.session_state.voice_answer,
                            "timestamp": st.session_state.get("timestamp", ""),
                            "skipped": False,
                            "evaluation": None,
                            "dont_know": False,
                            "is_follow_up": False
                        })
                        
                        # Evaluate the answer
                        persona_history = [h["evaluation"]["persona"] for h in st.session_state.history 
                                         if h.get("evaluation") and h["evaluation"].get("persona")]
                        
                        if is_technical:
                            evaluation_result = ai.evaluate_technical(role, question, st.session_state.voice_answer, persona_history)
                        else:
                            evaluation_result = ai.evaluate_behavioral(role, question, st.session_state.voice_answer, persona_history)
                        
                        # Update the last history item with evaluation
                        st.session_state.history[-1]["evaluation"] = evaluation_result
                        
                        st.session_state.current_question_idx += 1
                        # Reset recording state
                        keys_to_delete = [key for key in st.session_state.keys() if key.startswith("voice_")]
                        for key in keys_to_delete:
                            del st.session_state[key]
                        st.rerun()
                    else:
                        # Move to next question automatically and evaluate the answer
                        st.session_state.history.append({
                            "question": question,
                            "answer": st.session_state.voice_answer,
                            "timestamp": st.session_state.get("timestamp", ""),
                            "skipped": False,
                            "evaluation": None,
                            "dont_know": False,
                            "is_follow_up": False
                        })
                        
                        # Evaluate the answer
                        persona_history = [h["evaluation"]["persona"] for h in st.session_state.history 
                                         if h.get("evaluation") and h["evaluation"].get("persona")]
                        
                        if is_technical:
                            evaluation_result = ai.evaluate_technical(role, question, st.session_state.voice_answer, persona_history)
                        else:
                            evaluation_result = ai.evaluate_behavioral(role, question, st.session_state.voice_answer, persona_history)
                        
                        # Update the last history item with evaluation
                        st.session_state.history[-1]["evaluation"] = evaluation_result
                        
                        st.session_state.current_question_idx += 1
                        # Reset recording state
                        keys_to_delete = [key for key in st.session_state.keys() if key.startswith("voice_")]
                        for key in keys_to_delete:
                            del st.session_state[key]
                        st.rerun()
                except Exception as e:
                    # Error in AI evaluation, move to next question with fallback evaluation
                    st.session_state.history.append({
                        "question": question,
                        "answer": st.session_state.voice_answer,
                        "timestamp": st.session_state.get("timestamp", ""),
                        "skipped": False,
                        "evaluation": None,
                        "dont_know": False,
                        "is_follow_up": False
                    })
                    
                    # Use fallback evaluation
                    fallback_eval = ai._fallback_eval(st.session_state.voice_answer, st.session_state.get("is_follow_up", False))
                    st.session_state.history[-1]["evaluation"] = fallback_eval
                    
                    st.session_state.current_question_idx += 1
                    # Reset recording state
                    keys_to_delete = [key for key in st.session_state.keys() if key.startswith("voice_")]
                    for key in keys_to_delete:
                        del st.session_state[key]
                    st.rerun()
            else:
                # Fallback when AI is not available, move to next question
                is_follow_up = st.session_state.get("is_follow_up", False)
                st.session_state.history.append({
                    "question": question,
                    "answer": st.session_state.voice_answer,
                    "timestamp": st.session_state.get("timestamp", ""),
                    "skipped": False,
                    "evaluation": None,
                    "dont_know": False,
                    "is_follow_up": is_follow_up
                })
                
                # Use fallback evaluation
                fallback_eval = ai._fallback_eval(st.session_state.voice_answer, is_follow_up)
                st.session_state.history[-1]["evaluation"] = fallback_eval
                
                st.session_state.current_question_idx += 1
                # Reset recording state
                keys_to_delete = [key for key in st.session_state.keys() if key.startswith("voice_")]
                for key in keys_to_delete:
                    del st.session_state[key]
                st.rerun()


def feedback_panel():
    """Final feedback and report screen."""
    st.title("Interview Completed")
    st.success("Thank you for completing the interview!")
    
    # Show interview summary
    total_questions = len([q for q in st.session_state.history if not q.get("skipped", False)])
    st.info(f"You answered {total_questions} questions in this practice session.")
    
    # AI feedback message
    feedback_message = "Here's your detailed performance report with AI evaluation and feedback:"
    st.info(feedback_message)
    
    # Text-to-speech for feedback message
    if HAS_TTS:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say(feedback_message)
            engine.runAndWait()
        except Exception as e:
            pass
    
    st.info("Here's your detailed performance report:")
    
    FeedbackGenerator.generate_final_report(
        st.session_state.history,
        st.session_state.role,
        st.session_state.interview_type
    )
    
    st.markdown("---")
    
    # Ask if user wants to start a new interview
    st.info("Would you like to start a new interview practice session?")
    
    # Voice command for new interview
    st.markdown("### Voice Command")
    st.info("Click the button below and say 'yes' to start a new interview or 'no' to finish")
    
    if st.button("🎙 Respond", type="primary", use_container_width=True):
        with st.spinner("Listening for your response..."):
            try:
                import speech_recognition as sr
                # Create recognizer
                recognizer = sr.Recognizer()
                
                # Configure for human speech
                recognizer.pause_threshold = 1.0
                recognizer.non_speaking_duration = 0.5
                recognizer.dynamic_energy_threshold = False
                recognizer.energy_threshold = 400
                
                # Record from microphone
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    # Listen for up to 5 seconds
                    audio = recognizer.listen(source, phrase_time_limit=5)
                
                # Transcribe
                with st.spinner("Processing your response..."):
                    text = recognizer.recognize_google(audio).lower()
                    
                    # Check if user said "yes" or similar
                    yes_commands = ["yes", "yeah", "yep", "sure", "okay", "continue", "next", "restart"]
                    no_commands = ["no", "nope", "finish", "done", "exit", "quit"]
                    
                    if any(command in text for command in yes_commands):
                        # Reset all session state
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                    elif any(command in text for command in no_commands):
                        st.info("Thank you for using the AI Interview Practice Partner. Have a great day!")
                    else:
                        st.error("I didn't catch that. Please say 'yes' to start a new interview or 'no' to finish.")
                        
            except sr.WaitTimeoutError:
                st.error("No speech detected. Click the button again and respond clearly.")
            except sr.UnknownValueError:
                st.error("Could not understand audio. Please respond clearly.")
            except sr.RequestError as e:
                st.error(f"Service error: {e}")
            except Exception as e:
                st.error(f"Error processing response: {e}")
    
    # Fallback button
    if st.button("🔄 Start New Interview", use_container_width=True):
        # Reset all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="AI Interview Partner",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state variables
    if "stage" not in st.session_state:
        st.session_state.stage = "greeting"
    if "greeting_complete" not in st.session_state:
        st.session_state.greeting_complete = False
    if "role_selected" not in st.session_state:
        st.session_state.role_selected = False
    if "interview_type_selected" not in st.session_state:
        st.session_state.interview_type_selected = False
    
    # Route to appropriate panel
    if st.session_state.stage == "greeting":
        greeting_panel()
    elif st.session_state.stage == "role_selection":
        role_selection_panel()
    elif st.session_state.stage == "interview_type_selection":
        interview_type_selection_panel()
    elif st.session_state.stage == "setup":
        setup_panel()
    elif st.session_state.stage == "instructions":
        instructions_panel()
    elif st.session_state.stage == "generating_questions":
        generating_questions_panel()
    elif st.session_state.stage == "interview":
        interview_panel()
    elif st.session_state.stage == "feedback":
        feedback_panel()


if __name__ == "__main__":
    main()