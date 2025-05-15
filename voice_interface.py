import pyttsx3
import speech_recognition as sr

class VoiceInterface:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout=10):
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
            except sr.WaitTimeoutError:
                return None
        try:
            print("Recognizing...")
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "Speech recognition service is down."
