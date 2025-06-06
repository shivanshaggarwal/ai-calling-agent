from agent import AICallingAgent
import os
from dotenv import load_dotenv
import logging
from twilio.base.exceptions import TwilioRestException
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize the agent
        agent = AICallingAgent()
        
        # Get the phone number to call from environment variable
        to_number = os.getenv('TEST_PHONE_NUMBER')
        if not to_number:
            logger.error("TEST_PHONE_NUMBER not set in .env file")
            return
            
        # Add country code if not present
        if not to_number.startswith('+'):
            to_number = '+91' + to_number  # Assuming Indian number, adjust as needed
            
        # The Render URL
        render_url = 'https://ai-calling-agent-a35z.onrender.com'
        
        # Set up the TwiML URL
        twiml_url = f'{render_url}/twiml'
        
        logger.info(f"Making call to {to_number}")
        logger.info(f"TwiML URL: {twiml_url}")
        
        # Verify Twilio credentials
        if not agent.twilio_account_sid or not agent.twilio_auth_token:
            logger.error("Twilio credentials not properly set in .env file")
            return
            
        # Make the call
        call_sid = agent.make_outbound_call(
            to_number=to_number,
            twiml_url=twiml_url
        )
        
        if call_sid:
            logger.info(f"Call initiated successfully! Call SID: {call_sid}")
        else:
            logger.error("Failed to initiate call. Check your Twilio credentials and network connection.")
            
    except TwilioRestException as e:
        logger.error(f"Twilio API Error: {str(e)}")
        logger.error(f"More info: {e.uri}")
        if e.code == 21205:
            logger.error("This error usually means the phone number is not verified. Please verify your phone number in the Twilio console.")
    except Exception as e:
        logger.error(f"Error in test_call: {str(e)}")

if __name__ == '__main__':
    main() 