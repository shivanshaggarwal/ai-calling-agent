from flask import Flask, request, Response
import os
from dotenv import load_dotenv
import logging
from urllib.parse import unquote
from datetime import datetime
from agent import AICallingAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

agent = AICallingAgent()

@app.route('/')
def index():
    return "AI Calling Agent is running!"

@app.route('/twiml', methods=['GET', 'POST'])
def twiml():
    try:
        if request.method == 'GET':
            initial_message = "Hello! How can I assist you today?"
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Gather input="speech" action="/twiml" method="POST">
            <Say>{initial_message}</Say>
        </Gather>
    </Response>"""
            return Response(twiml, mimetype='text/xml')

        elif request.method == 'POST':
            speech_result = request.form.get('SpeechResult', '')
            if speech_result:
                response = agent.process_conversation(speech_result)
                if "bye" in speech_result.lower():
                    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
        <Say>{response}</Say>
        <Hangup/>
</Response>"""
                else:
                    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
        <Gather input="speech" action="/twiml" method="POST">
            <Say>{response}</Say>
        </Gather>
</Response>"""
                return Response(twiml, mimetype='text/xml')
            else:
                twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>I didn't catch that. Please speak again.</Say>
    <Gather input="speech" action="/twiml" method="POST"/>
</Response>"""
                return Response(twiml, mimetype='text/xml')
    except Exception as e:
        logger.error(f"Error in TwiML handling: {str(e)}")
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, there was an error processing your request.</Say></Response>',
            mimetype='text/xml', status=500)

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check requested")
    return Response("OK", status=200)

if __name__ == '__main__':
    load_dotenv()
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 10000))
    logger.info(f"Starting server on port {port}")
    # Run the server
    app.run(host='0.0.0.0', port=port) 