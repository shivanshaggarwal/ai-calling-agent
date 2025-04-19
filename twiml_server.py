from flask import Flask, request, Response
import os
from dotenv import load_dotenv
import logging
from urllib.parse import unquote
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store conversation state
conversation_state = {}

@app.route('/twiml', methods=['GET'])
def get_twiml():
    try:
        # Get the call SID from the request
        call_sid = request.args.get('CallSid')
        if not call_sid:
            call_sid = f"call-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        # Initialize conversation state if not exists
        if call_sid not in conversation_state:
            conversation_state[call_sid] = {
                "stage": "greeting",
                "last_response": "Hello! I am your AI assistant. How can I help you today?",
                "history": []
            }
            
        # Get the current state
        state = conversation_state[call_sid]
        
        # Generate TwiML based on the current stage
        if state["stage"] == "greeting":
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/handle-input" method="POST">
        <Say>{state["last_response"]}</Say>
    </Gather>
</Response>"""
        else:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/handle-input" method="POST">
        <Say>{state["last_response"]}</Say>
    </Gather>
</Response>"""
        
        logger.info(f"Generated TwiML for call {call_sid} at stage {state['stage']}")
        return Response(twiml, mimetype='text/xml')
    except Exception as e:
        logger.error(f"Error generating TwiML: {str(e)}")
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, there was an error processing your request.</Say></Response>',
            mimetype='text/xml',
            status=500
        )

@app.route('/handle-input', methods=['POST'])
def handle_input():
    try:
        # Get the call SID and speech result
        call_sid = request.form.get('CallSid')
        speech_result = request.form.get('SpeechResult', '')
        
        if not call_sid:
            return Response(
                '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, I could not process your request.</Say></Response>',
                mimetype='text/xml'
            )
            
        # Get the current state
        state = conversation_state.get(call_sid, {
            "stage": "greeting",
            "last_response": "Hello! I am your AI assistant. How can I help you today?",
            "history": []
        })
        
        # Add to conversation history
        state["history"].append({
            "role": "user",
            "content": speech_result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process the input and generate response
        # This is a simple example - in a real implementation, you would use your AI model
        if "bye" in speech_result.lower():
            response = "Goodbye! Thank you for calling."
            state["stage"] = "end"
        elif "help" in speech_result.lower():
            response = "I can help you with various tasks. What would you like assistance with?"
            state["stage"] = "help"
        else:
            response = f"I understand you said: {speech_result}. How can I assist you further?"
            state["stage"] = "conversation"
            
        # Update the state
        state["last_response"] = response
        state["history"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        conversation_state[call_sid] = state
        
        # Generate TwiML for the next interaction
        if state["stage"] == "end":
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{response}</Say>
    <Hangup/>
</Response>"""
        else:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/handle-input" method="POST">
        <Say>{response}</Say>
    </Gather>
</Response>"""
            
        logger.info(f"Processed input for call {call_sid}: {speech_result}")
        return Response(twiml, mimetype='text/xml')
    except Exception as e:
        logger.error(f"Error handling input: {str(e)}")
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, there was an error processing your input.</Say></Response>',
            mimetype='text/xml',
            status=500
        )

@app.route('/status-callback', methods=['POST'])
def status_callback():
    try:
        # Log the call status
        call_sid = request.form.get('CallSid')
        call_status = request.form.get('CallStatus')
        logger.info(f"Call {call_sid} status: {call_status}")
        
        # Clean up conversation state if call is completed
        if call_status in ['completed', 'failed', 'busy', 'no-answer']:
            if call_sid in conversation_state:
                del conversation_state[call_sid]
                
        return Response("OK", status=200)
    except Exception as e:
        logger.error(f"Error in status callback: {str(e)}")
        return Response("Error", status=500)

@app.route('/health', methods=['GET'])
def health_check():
    return Response("OK", status=200)

if __name__ == '__main__':
    load_dotenv()
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 10000))
    # Run the server
    app.run(host='0.0.0.0', port=port) 