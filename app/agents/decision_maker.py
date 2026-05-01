from app.models.schemas import ReviewState


def choose_decision(severity: str, style_score: float) -> str:
    if severity in ("critical", "high"):
        return "request_changes"
    if severity == "medium" or style_score < 70:
        return "comment"
    return "approve"


def decision_node(state: ReviewState) -> dict:
    decision = choose_decision(state.severity, state.score)
    return {"decision": decision}
