from app.models.schemas import ReviewState


def write_review(state: ReviewState) -> dict:
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