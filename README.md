# AI Calling Agent

An AI-powered calling agent that can understand and speak in both English and Hindi. It uses free and open-source components for speech recognition, synthesis, and natural language processing.

## Features

- Speech recognition using OpenAI's Whisper (open source)
- Text-to-speech synthesis using gTTS
- Support for both English and Hindi languages
- Real-time audio processing
- Twilio integration for outbound calling
- Extensible conversation processing using Mistral

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Twilio credentials:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
TEST_PHONE_NUMBER=your_test_phone_number
```

## Local Development

1. Start the TwiML server:
```bash
python twiml_server.py
```

2. Test the calling agent:
```bash
python test_call.py
```

3. Run the interactive conversation:
```bash
python agent.py
```

## Deployment to Render.com

1. Create a new account on [Render.com](https://render.com)

2. Create a new Web Service:
   - Connect your GitHub repository
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python twiml_server.py`

3. Add the following environment variables in Render:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `PORT`: 10000

4. After deployment, update your `.env` file with the Render URL:
```
RENDER_URL=https://your-app-name.onrender.com
```

## Requirements

- Python 3.8+
- FFmpeg
- Twilio account
- See requirements.txt for full dependency list

## License

This project is open source and available under the MIT License. 