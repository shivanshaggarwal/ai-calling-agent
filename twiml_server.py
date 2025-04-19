from flask import Flask, request, Response
from agent import AICallingAgent
import os
from dotenv import load_dotenv
import logging
from waitress import serve

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
agent = AICallingAgent()

@app.route('/twiml', methods=['GET'])
def get_twiml():
    try:
        # Get the text to speak from query parameter
        text = request.args.get('text', 'Hello, this is an automated call.')
        logger.info(f"Generating TwiML for text: {text}")
        
        # Generate TwiML response
        twiml = agent.generate_twiml(text)
        
        # Return as XML response
        return Response(twiml, mimetype='text/xml')
    except Exception as e:
        logger.error(f"Error generating TwiML: {str(e)}")
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, there was an error processing your request.</Say></Response>',
            mimetype='text/xml',
            status=500
        )

@app.route('/health', methods=['GET'])
def health_check():
    return Response("OK", status=200)

if __name__ == '__main__':
    load_dotenv()
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 5000))
    # Run the server using waitress for production
    serve(app, host='0.0.0.0', port=port) 