import requests

BASE_URL = "http://127.0.0.1:8000"

class MentorAgent:
    def __init__(self):
        self.name = "mentor_agent"

    def ask_mentor(self, question):
        """Calls the API to get an answer for a mentor-related query."""
        response = requests.post(f"{BASE_URL}/mentor_interaction/", json={"question": question})
        
        if response.status_code == 200:
            return response.json()["answer"]
        return "Error fetching response from mentor bot."

# Initialize agent instance
mentor_agent = MentorAgent()