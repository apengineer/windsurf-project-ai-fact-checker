import json
import pytest
from unittest.mock import patch, MagicMock

# Test the home route
def test_home_route(client):
    """Test that the home route returns the index.html file."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.content_type

# Test the fact-check endpoint with missing claim
def test_fact_check_missing_claim(client):
    """Test the fact-check endpoint with missing claim."""
    response = client.post('/api/fact-check', 
                         data=json.dumps({}),
                         content_type='application/json')
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)

# Test the search_guardian_api function
@patch('app.requests.get')
def test_search_guardian_api(mock_get, app):
    """Test the search_guardian_api function returns articles."""
    # Mock the response from the Guardian API
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'response': {
            'results': [
                {'webTitle': 'Test Article', 'webUrl': 'http://example.com', 'fields': {'bodyText': 'Test content'}}
            ]
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    with app.app_context():
        from app import search_guardian_api
        articles = search_guardian_api("test claim")
        assert len(articles) == 1
        assert articles[0]['webTitle'] == 'Test Article'

# Test the fact_check_with_claude function with mock
@patch('app.anthropic_client.messages.create')
def test_fact_check_with_claude(mock_claude, app):
    """Test the fact_check_with_claude function with a mock response."""
    # Mock the Claude API response
    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = """```json
    {
        "credibility_score": 85,
        "reasoning": "Test reasoning",
        "supporting_articles": [
            {
                "title": "Test Article",
                "url": "http://example.com",
                "relevance": "Relevant to the claim"
            }
        ]
    }
    ```"""
    mock_claude.return_value = mock_message

    with app.app_context():
        from app import fact_check_with_claude
        test_articles = [
            {'webTitle': 'Test Article', 'webUrl': 'http://example.com', 'fields': {'bodyText': 'Test content'}}
        ]
        result = fact_check_with_claude("test claim", test_articles)
        assert 'credibility_score' in result
        assert 'reasoning' in result
        assert 'supporting_articles' in result
        assert result['credibility_score'] == 85

# Test the fact-check endpoint with a valid claim
@patch('app.search_guardian_api')
@patch('app.fact_check_with_claude')
def test_fact_check_valid_claim(mock_fact_check, mock_search, client, app):
    """Test the fact-check endpoint with a valid claim."""
    # Mock the search_guardian_api response
    mock_search.return_value = [
        {'webTitle': 'Test Article', 'webUrl': 'http://example.com', 'fields': {'bodyText': 'Test content'}}
    ]
    
    # Mock the fact_check_with_claude response
    mock_fact_check.return_value = {
        'credibility_score': 85,
        'reasoning': 'Test reasoning',
        'supporting_articles': [
            {
                'title': 'Test Article',
                'url': 'http://example.com',
                'relevance': 'Relevant to the claim'
            }
        ]
    }
    
    # Make the request
    response = client.post('/api/fact-check',
                         data=json.dumps({'claim': 'test claim'}),
                         content_type='application/json')
    
    # Verify the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'credibility_score' in data
    assert data['credibility_score'] == 85
    assert 'reasoning' in data
    assert 'related_articles' in data
    assert 'supporting_articles' in data
