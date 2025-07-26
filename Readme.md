# AI Fact-Checking Platform

An AI-driven fact-checking platform for news editors that verifies claims by checking against reliable news sources and analyzing the context.

## Features

- AI-powered credibility scoring using Anthropic's Claude
- Advanced reasoning and analysis
- Integration with Guardian News API
- Related article suggestions

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory and add your API keys:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GUARDIAN_API_KEY=your_guardian_api_key_here
```

3. Run the backend server:
```bash
python app.py
```

4. Open `index.html` in your web browser to access the frontend using http://localhost:5000

## Usage

1. Enter a claim in the text area
2. Click "Check Claim"
3. View the credibility score and detailed analysis

## Technology Stack

- Backend: Python Flask
- AI: Anthropic's Claude
- Frontend: HTML/CSS/JavaScript
- News API: The Guardian

## Testing

To run the test suite, use the following command:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests with coverage report
pytest
```

This will run all tests and generate a coverage report showing which parts of your code are covered by tests.

## Example video of backend app

You see the app started, request is send with a claim "AI replaces human" that returns credibility score of 30 and related articles from Guardian API. Next you see the claim "AI is dead" returns a credibility score of 0 and no related articles. 

https://github.com/user-attachments/assets/b1c427ad-0f59-4431-a9c1-0165d723e877



