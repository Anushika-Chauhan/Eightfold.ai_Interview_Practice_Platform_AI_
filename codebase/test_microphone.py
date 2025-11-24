import speech_recognition as sr

# Test microphone access
try:
    recognizer = sr.Recognizer()
    print("Recognizer created successfully")
    
    # List available microphones
    print("Available microphones:")
    for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {i}: {mic_name}")
    
    # Test microphone access
    with sr.Microphone() as source:
        print("Microphone accessed successfully")
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for 5 seconds...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        print("Audio captured successfully")
        
        # Try to recognize
        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: {text}")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            
except Exception as e:
    print(f"Error: {e}")