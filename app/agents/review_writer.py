import os
import httpx
from app.models.schemas import ReviewState


def write_review(state: ReviewState) -> dict:
    if state.parse_error:
        comment = "## AI Code Review\n\n⚠️ **Error**: Failed to parse the code diff correctly. Deep analysis was skipped."
        return {"comment": comment}

    comment = "## AI Code Review\n\n"

    comment += "### Security Findings\n"
    if len(state.security) == 0:
        comment += "- No security issues found.\n"
    else:
        for item in state.security:
            comment += "- [" + item["severity"].upper() + "] "
            comment += item["description"]
            comment += "\nFix: " + item["suggested_fix"] + "\n"

    comment += "\n### Style Compliance: " + str(round(state.score)) + "/100\n"
    for item in state.style[:5]:
        comment += "- " + item["rule"] + ": " + item["description"] + "\n"

    comment += "\n### Refactor Suggestions\n"
    for item in state.refactor[:3]:
        comment += "- [" + item["type"] + "] " + item["description"] + "\n"

    return {"comment": comment}


def post_github_review_node(state: ReviewState) -> dict:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"github_review_id": None}

    # Decide event type
    event = "COMMENT"
    if state.decision == "request_changes":
        event = "REQUEST_CHANGES"
    elif state.decision == "approve":
        event = "APPROVE"

    try:
        url = f"https://api.github.com/repos/{state.repo}/pulls/{state.pr}/reviews"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        payload = {
            "body": state.comment,
            "event": event
        }
        
        with httpx.Client() as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {"github_review_id": data.get("id")}
    except Exception as e:
        print(f"Error posting to GitHub: {e}")
        return {"github_review_id": None}