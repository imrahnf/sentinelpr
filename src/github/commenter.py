from typing import List, Dict
from src.github.client import GitHubClient

class PRCommenter:
    def __init__(self, repo: str, pr_number: int, token: str):
        self.client = GitHubClient(token, repo, pr_number)

    def post_comments(self, reviews: List[Dict]):
        # Converts internal review objects into GitHub API comments.
        gh_comments = []

        for review in reviews:
            # We skip 'Global' comments that don't have a specific line number
            if not review.get('line'):
                continue

            # Format the body with emoji and severity
            severity_icon = "🔴" if review.get('severity') == "HIGH" else "⚠️"
            body = (
                f"**{severity_icon} {review.get('severity', 'UNKNOWN')} Priority**\n"
                f"{review.get('issue')}\n\n"
                f"**Suggestion:** `{review.get('suggestion')}`"
            )

            gh_comments.append({
                "path": review['file_path'],    # Must match the filename in the Diff
                "line": int(review['line']),    # Must be the line in the NEW file
                "side": "RIGHT",                # RIGHT = The new code
                "body": body
            })

        if gh_comments:
            self.client.post_review(gh_comments)