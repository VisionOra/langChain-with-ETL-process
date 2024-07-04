import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RapidApiLIProfileClient:
    def __init__(self):
        self.base_url = "https://linkedin-data-api.p.rapidapi.com/"
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = os.getenv('RAPIDAPI_HOST')
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }
    
    def get_user_data(self, username):
        print(f"Calling the RapidAPi for username {username}")
        response = self._make_request({"username": username})
        print(f"Response: {response.json()}")
        return self._handle_response(response)
    
    def _make_request(self, params):
        return requests.get(self.base_url, headers=self.headers, params=params)
    
    def _handle_response(self, response):
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()