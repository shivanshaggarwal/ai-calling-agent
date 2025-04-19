from flask import Flask, request, Response
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/twiml', methods=['GET'])
def get_twiml():
    try:
        # Get the text to speak from query parameter
        text = request.args.get('text', 'Hello, this is an automated call.')
        logger.info(f"Generating TwiML for text: {text}")
        
        # Generate TwiML response
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{text}</Say>
</Response>"""
        
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
    port = int(os.getenv('PORT', 10000))
    # Run the server
    app.run(host='0.0.0.0', port=port) 