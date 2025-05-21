from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import anthropic
import json

load_dotenv('.env')

app = Flask(__name__)

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
print("API Key loaded:", "***" + os.getenv('ANTHROPIC_API_KEY')[-5:])  # Mask most of the key for security

# Helper function to search Guardian API
def search_guardian_api(claim):
    search_params = {
        'q': claim,
        'show-fields': 'bodyText',
        'api-key': GUARDIAN_API_KEY,
        'order-by': 'relevance',
        'page-size': 5,
        'from-date': '2025-01-01',
        'to-date': '2025-05-21',
    }
    
    try:
        response = requests.get(GUARDIAN_API_URL, params=search_params)
        response.raise_for_status()
        data = response.json()
        articles = data.get('response', {}).get('results', [])
        return articles
    except Exception as e:
        print(f"Error searching Guardian API: {str(e)}")
        return []

# Helper function for fact-checking with Claude
def fact_check_with_claude(claim, articles):
    # Format articles for Claude
    article_summary = "\n".join([
        f"- {article.get('webTitle', 'Untitled')} ({article.get('webUrl', '')})" 
        for article in articles
    ])
    
    article_body = "\n".join([
        f"- {article.get('webTitle', 'Untitled')} {article.get('webUrl', '')}  {article.get('fields').get('bodyText')}"
        for article in articles
    ])

    # print(f"Article body: {article_body}")
    

    prompt = f"""You are a fact-checking assistant. Please analyze the following claim in context of these recent news articles:
    
    Claim: {claim}
    
    Recent News Articles:
    {article_body}
    
    Please provide:
    1. A credibility score (0-100) based on how well the claim aligns with recent news
    2. Detailed reasoning explaining your score
    3. Specific references to relevant articles that support your analysis

    Format your response as JSON:
    {{
        "credibility_score": <score>,
        "reasoning": "<detailed explanation>",
        "supporting_articles": [
            {{
                "title": "<article title>",
                "url": "<article url>",
                "relevance": "<why this article is relevant>"
            }}
        ]
    }}
    """
    
    try:
        response = anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=5000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract text from TextBlock
        text_block = response.content[0]
        text = text_block.text
        
        # Extract JSON from code block
        json_str = text.split('```json')[1].split('```')[0].strip()
        
        # Print extracted JSON for debugging
        print(f"Extracted JSON: {json_str}")
        
        # Parse the JSON string
        try:
            json_data = json.loads(json_str)
            print(f"Parsed JSON data: {json_data}")
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in fact_check_with_claude: {str(e)}")
            return {
                "credibility_score": 50,
                "reasoning": f"Could not parse Claude's response as JSON: {str(e)}",
                "supporting_articles": []
            }
    except Exception as e:
        print(f"Error processing response fact_check_with_claude: {str(e)}")
        return {
            "credibility_score": 50,
            "reasoning": f"Error processing response fact_check_with_claude: {str(e)}",
            "supporting_articles": []
        }

# Guardian API configuration
GUARDIAN_API_KEY = os.getenv('GUARDIAN_API_KEY')
GUARDIAN_API_URL = "https://content.guardianapis.com/search"

@app.route('/api/fact-check', methods=['POST'])
def fact_check():
   
    # Get claim from JSON body
    data = request.get_json()
    claim = data.get('claim', '')
    print(f"Claim received: {claim}")
        
    if not claim:
        return jsonify({"error": "No claim provided"}), 400
    
    try:
        # 1. Search Guardian API for recent articles
        print("Searching Guardian API...")
        articles = search_guardian_api(claim)
        print(f"Found {len(articles)} related articles")
        
        # 2. Analyze claim with Claude using the context from articles
        print("Analyzing claim with Claude...")
        claude_json = fact_check_with_claude(claim, articles)
                            
        # 3. Prepare response
        result = {
           'credibility_score': claude_json.get('credibility_score', 50),
           'reasoning': claude_json.get('reasoning', 'No reasoning provided'),
           'related_articles': articles,
           'supporting_articles': claude_json.get('supporting_articles', [])
        }

        
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500


    return jsonify(result)

# Serve static files
@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
