import pytest
import os
from dotenv import load_dotenv
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file for testing
load_dotenv('.env')

# Test configuration
@pytest.fixture
def app():
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

# Mock for Guardian API responses
@pytest.fixture
def mock_guardian_response():
    return {
        'response': {
            'results': [
                {
                    'webTitle': 'Test Article 1',
                    'webUrl': 'https://example.com/article1',
                    'fields': {
                        'bodyText': 'This is a test article body text.'
                    }
                },
                {
                    'webTitle': 'Test Article 2',
                    'webUrl': 'https://example.com/article2',
                    'fields': {
                        'bodyText': 'Another test article with different content.'
                    }
                }
            ]
        }
    }
