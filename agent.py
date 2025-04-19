import whisper
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
import tempfile
import os
import requests
import json
from typing import Optional, Dict, List
import re
import ollama
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

class AICallingAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Twilio client
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        
        # Initialize Whisper model for speech recognition
        self.whisper_model = whisper.load_model("base")
        self.language = "en"  # default language
        self.temp_dir = Path(tempfile.gettempdir())
        
        # Set FFmpeg path
        ffmpeg_path = Path("ffmpeg-2025-04-17-git-7684243fbe-full_build/bin/ffmpeg.exe")
        if not ffmpeg_path.exists():
            ffmpeg_path = Path("ffmpeg/bin/ffmpeg.exe")
        if ffmpeg_path.exists():
            os.environ["PATH"] = str(ffmpeg_path.parent) + os.pathsep + os.environ["PATH"]
            
        # Initialize conversation context
        self.conversation_history: List[Dict[str, str]] = []
        self.context_window = 5  # Number of previous messages to keep in context
        
        # Initialize Ollama with Mistral
        self.ollama_model = "mistral"  # Using Mistral model
        self._ensure_ollama_model()
        
        # Business logic state
        self.call_state = {
            "current_stage": "greeting",
            "customer_info": {},
            "last_interaction": datetime.now(),
            "call_duration": 0
        }

    def _ensure_ollama_model(self):
        """Ensure the Ollama model is available"""
        try:
            # Try to pull the model if not available
            ollama.pull(self.ollama_model)
        except Exception as e:
            print(f"Warning: Could not pull Ollama model: {e}")
            print("Please make sure Ollama is running and the model is available")

    def set_language(self, language: str):
        """Set the language for the agent (en/hi)"""
        if language not in ["en", "hi"]:
            raise ValueError("Language must be 'en' for English or 'hi' for Hindi")
        self.language = language

    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        # Simple rule-based language detection
        hindi_chars = re.compile(r'[\u0900-\u097F]')
        if hindi_chars.search(text):
            return "hi"
        return "en"

    def listen(self, duration: int = 5) -> str:
        """Record audio and convert to text"""
        print(f"Recording for {duration} seconds...")
        
        # Record audio
        recording = sd.rec(
            int(duration * 16000),
            samplerate=16000,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        # Save recording temporarily
        temp_file = self.temp_dir / "temp_recording.wav"
        sf.write(temp_file, recording, 16000)
        
        # Transcribe with Whisper
        result = self.whisper_model.transcribe(str(temp_file))
        return result["text"]

    def speak(self, text: str, output_file: Optional[str] = None):
        """Convert text to speech"""
        # Detect language of the response
        response_lang = self.detect_language(text)
        
        # Use appropriate TTS based on language
        if response_lang == "hi":
            # For Hindi, we can use Google's Hindi TTS
            tts = gTTS(text=text, lang='hi')
        else:
            tts = gTTS(text=text, lang='en')
        
        if output_file is None:
            output_file = self.temp_dir / "temp_speech.mp3"
        
        tts.save(str(output_file))
        return str(output_file)

    def update_call_state(self, user_input: str):
        """Update the call state based on user input"""
        # Update last interaction time
        self.call_state["last_interaction"] = datetime.now()
        
        # Simple state machine for call flow
        if self.call_state["current_stage"] == "greeting":
            if any(word in user_input.lower() for word in ["help", "assist", "support"]):
                self.call_state["current_stage"] = "needs_assessment"
            elif any(word in user_input.lower() for word in ["product", "service", "buy"]):
                self.call_state["current_stage"] = "product_info"
        
        # Add more state transitions based on your business logic

    def process_conversation(self, text: str) -> str:
        """Process the conversation and generate response using Mistral"""
        # Detect input language
        input_lang = self.detect_language(text)
        
        # Update call state
        self.update_call_state(text)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": text,
            "language": input_lang
        })
        
        # Keep only the last N messages
        if len(self.conversation_history) > self.context_window:
            self.conversation_history = self.conversation_history[-self.context_window:]
        
        try:
            # Prepare the conversation context for Mistral
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant that can speak both English and Hindi. 
                    Current call stage: {self.call_state['current_stage']}
                    Respond in the same language as the user's input.
                    Be professional and helpful.
                    If the user switches language, respond in that language."""
                }
            ]
            
            # Add conversation history
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Get response from Mistral
            response = ollama.chat(
                model=self.ollama_model,
                messages=messages
            )
            
            # Extract the response text
            response_text = response['message']['content']
            
        except Exception as e:
            print(f"Error getting Mistral response: {e}")
            # Fallback to simple responses based on call stage
            if self.call_state["current_stage"] == "greeting":
                response_text = "Hello! How can I help you today?"
            elif self.call_state["current_stage"] == "needs_assessment":
                response_text = "What kind of assistance do you need?"
            elif self.call_state["current_stage"] == "product_info":
                response_text = "Which product or service would you like to know more about?"
            else:
                response_text = "I understand you said: " + text
        
        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text,
            "language": self.detect_language(response_text)
        })
        
        return response_text

    def run_conversation(self, duration: int = 5):
        """Run a full conversation loop"""
        print("Starting conversation...")
        print("You can speak in either English or Hindi.")
        print("Say 'bye' to end the conversation.")
        
        while True:
            # Listen to user
            user_input = self.listen(duration)
            if not user_input.strip():
                continue
                
            print(f"User said: {user_input}")
            
            # Process and generate response
            response = self.process_conversation(user_input)
            print(f"Agent response: {response}")
            
            # Speak the response
            speech_file = self.speak(response)
            
            # If user says bye, end conversation
            if "bye" in user_input.lower():
                break

    def make_outbound_call(self, to_number: str, twiml_url: str):
        """Make an outbound call using Twilio"""
        try:
            # For trial accounts, we need to use a verified phone number
            if not to_number.startswith('+'):
                to_number = '+91' + to_number  # Assuming Indian number
            
            call_params = {
                'to': to_number,
                'from_': self.twilio_phone_number,
                'url': twiml_url,
                'status_callback': f'{twiml_url}/status-callback',
                'status_callback_event': ['initiated', 'ringing', 'answered', 'completed']
            }
            
            # Log the call parameters (excluding sensitive data)
            print(f"Making call to {to_number}")
            print(f"Using TwiML URL: {twiml_url}")
            
            call = self.twilio_client.calls.create(**call_params)
            print(f"Call initiated with SID: {call.sid}")
            return call.sid
        except Exception as e:
            print(f"Error making outbound call: {e}")
            if hasattr(e, 'code') and e.code == 21205:
                print("This error usually means the phone number is not verified. Please verify your phone number in the Twilio console.")
            return None

    def generate_twiml(self, text: str) -> str:
        """Generate TwiML for the call"""
        # Convert text to speech and get the URL
        speech_file = self.speak(text)
        # In a real implementation, you would upload this file to a web server
        # and return the URL. For now, we'll return a simple TwiML response
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{text}</Say>
</Response>"""

if __name__ == "__main__":
    # Example usage
    agent = AICallingAgent()
    twiml = agent.generate_twiml("Hello, this is an automated call.")
    call_sid = agent.make_outbound_call("+919911324046", "https://your-server.com/twiml")
    # For Hindi
    # agent.set_language("hi")
    
    print("Starting conversation...")
    agent.run_conversation() 