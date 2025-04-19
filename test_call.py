from agent import AICallingAgent
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize the agent
        agent = AICallingAgent()
        
        # Get the phone number to call from environment variable or use a default
        to_number = os.getenv('TEST_PHONE_NUMBER', '+1234567890')
        
        # Get the Render URL from environment variable
        render_url = os.getenv('RENDER_URL', 'https://ai-calling-agent.onrender.com')
        twiml_url = f'{render_url}/twiml?text=Hello, this is a test call from the AI calling agent.'
        
        logger.info(f"Making call to {to_number} using TwiML URL: {twiml_url}")
        call_sid = agent.make_outbound_call(to_number, twiml_url)
        
        if call_sid:
            logger.info(f"Call initiated successfully! Call SID: {call_sid}")
        else:
            logger.error("Failed to initiate call. Check your Twilio credentials and network connection.")
    except Exception as e:
        logger.error(f"Error in test_call: {str(e)}")

if __name__ == '__main__':
    main() 