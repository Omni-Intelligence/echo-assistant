# Echo Assist

A desktop voice assistant powered by OpenAI that allows natural conversations with customizable AI voices.

## Features

* Voice-activated interface with space bar or button press control
* Real-time speech-to-text processing
* AI-powered responses using OpenAI
* Multiple high-quality voice options:
  * Alloy - Neutral and balanced
  * Ash - Warm and elderly 
  * Ballad - Melodic and bright
  * Coral - Warm and mature
  * Echo - Neutral and clear
  * Sage - Serious and deep
  * Shimmer - Bright and young
* Text response display with copy functionality
* Recording duration timer
* Simple and modern UI design

## Requirements

* Python 3.8+
* PyQt6
* OpenAI API key
* Microphone for voice input
* Speakers/headphones for audio output

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Omni-Intelligence/echo-assistant.git
cd echo-assistant
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Select your preferred AI voice from the dropdown menu
3. Press the microphone button or spacebar to start recording
4. Speak your question or command
5. Press again to stop recording and get the AI response
6. View the text response and hear the audio reply

## License

MIT License