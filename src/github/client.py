import os
import requests
from typing import List, Dict

class GitHubClient:
    def __init__(self, token: str, repo: str, pr_number: int):
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.pr_number = pr_number
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def post_review(self, comments: List[Dict]):
        # Batches multiple comments into a single Review payload.
        # This prevents sending 10 separate emails for 10 bugs.
        
        if not comments:
            print("No comments to post.")
            return

        url = f"{self.base_url}/pulls/{self.pr_number}/reviews"
        
        payload = {
            "body": "### SentinelPR Scan Results\nI have analyzed your changes. Here are my findings:",
            "event": "COMMENT", # We comment, we don't 'REQUEST_CHANGES' (which blocks merging)
            "comments": comments
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Posted review with {len(comments)} comments.")
        except requests.exceptions.HTTPError as e:
            print(f"Failed to post review: {e}")
            print(f"Response: {e.response.text}")