"""
Audio Processing and Voice Recognition.
Handles voice recording, speech-to-text conversion.
"""

import streamlit as st

try:
    import speech_recognition as sr
    HAS_SR = True
except Exception:
    HAS_SR = False


def record_voice_answer(reset_state=False) -> str:
    """
    Record voice answer using microphone and convert to text.

    Args:
        reset_state: Whether to reset the recording state

    Returns:
        Transcribed text from speech
    """
    st.markdown("### Voice Recording")
    
    # Reset state if requested
    if reset_state:
        keys_to_delete = list(st.session_state.keys())
        for key in keys_to_delete:
            if key.startswith("voice_"):
                del st.session_state[key]
    
    # Initialize session state variables
    if "voice_answer" not in st.session_state:
        st.session_state.voice_answer = ""
    if "voice_recording_complete" not in st.session_state:
        st.session_state.voice_recording_complete = False

    # Primary: Microphone recording
    if HAS_SR:
        st.info("🎤 I'm listening for your answer. Please speak clearly now.")
        
        # Show recorded answer if available
        if st.session_state.voice_recording_complete:
            st.success("Your recorded answer:")
            st.text_area("Answer:", st.session_state.voice_answer, height=150, disabled=True)
            return st.session_state.voice_answer
        
        # Automatically start recording without button click
        with st.spinner("🔴 Recording... Speak now! (Up to 3 minutes)"):
            try:
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
                    # Listen for up to 3 minutes
                    audio = recognizer.listen(source, phrase_time_limit=180)

                # Transcribe
                with st.spinner("Converting speech to text..."):
                    text = recognizer.recognize_google(audio)
                    st.session_state.voice_answer = text
                    st.session_state.voice_recording_complete = True
                    st.success("✅ Answer recorded successfully!")

            except sr.WaitTimeoutError:
                st.error("No speech detected. Please refresh the page and try again.")
                st.session_state.voice_answer = "[No speech detected]"
                st.session_state.voice_recording_complete = True
            except sr.UnknownValueError:
                st.error("Could not understand audio. Please speak more clearly.")
                st.session_state.voice_answer = "[Could not understand audio]"
                st.session_state.voice_recording_complete = True
            except sr.RequestError as e:
                st.error(f"Service error: {e}")
                st.session_state.voice_answer = "[Service unavailable]"
                st.session_state.voice_recording_complete = True
            except Exception as e:
                st.error(f"Recording failed: {e}")
                st.session_state.voice_answer = "[Recording failed]"
                st.session_state.voice_recording_complete = True
                
            # Rerun to show the recorded answer
            st.rerun()
            
    else:
        st.warning("Microphone not available. Please install: pip install SpeechRecognition pyaudio")
        fallback_text = st.text_area("Type your answer:", height=150)
        return fallback_text

    return ""