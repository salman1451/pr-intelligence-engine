import os
import time
import uuid
import httpx

from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph

from app.agents.security_reviewer import security_node
from app.agents.diff_parser import parse_diff_node, should_analyze_code
from app.agents.style_reviewer import style_node
from app.agents.refactor_reviewer import refactor_node
from app.agents.review_writer import write_review, post_github_review_node
from app.agents.decision_maker import decision_node
from app.models.schemas import ReviewRequest, ReviewResponse, ReviewState

load_dotenv()


def build_graph():
    builder = StateGraph(ReviewState)

    builder.add_node("parse_diff", parse_diff_node)
    builder.add_node("security", security_node)
    builder.add_node("style", style_node)
    builder.add_node("refactor", refactor_node)
    builder.add_node("decision", decision_node)
    builder.add_node("write_review", write_review)
    builder.add_node("post_github", post_github_review_node)

    builder.add_edge(START, "parse_diff")

    builder.add_conditional_edges(
        "parse_diff",
        should_analyze_code,
        {
            "analyze": "security",
            "skip": "decision",
        },
    )

    builder.add_edge("security", "style")
    builder.add_edge("style", "refactor")
    builder.add_edge("refactor", "decision")
    builder.add_edge("decision", "write_review")
    builder.add_edge("write_review", "post_github")
    builder.add_edge("post_github", END)

    return builder.compile()


graph = build_graph()


def review_pull_request(request: ReviewRequest) -> ReviewResponse:
    start = time.perf_counter()

    initial_state = ReviewState(
        run_id=str(uuid.uuid4()),
        pr=request.pr,
        repo=request.repo,
        title=request.title,
        desc=request.desc or "",
        raw_diff=request.raw_diff,
    )

    result_dict = graph.invoke(initial_state)
    
    state = ReviewState(**result_dict)

    duration = round(time.perf_counter() - start, 2)
    
    # Bug 1 Fix: n8n callback
    if request.n8n_callback_url:
        try:
            with httpx.Client() as client:
                client.post(request.n8n_callback_url, json={
                    "run_id": state.run_id,
                    "pr": state.pr,
                    "repo": state.repo,
                    "decision": state.decision,
                    "comment": state.comment,
                    "security_count": len(state.security),
                    "severity": state.severity,
                    "score": state.score,
                    "duration_ms": int(duration * 1000)
                })
        except Exception as e:
            print(f"Error calling n8n callback: {e}")

    return ReviewResponse(
        run_id=state.run_id,
        pr=state.pr,
        decision=state.decision,
        severity=state.severity,
        score=state.score,
        github_review_id=state.github_review_id,
        comment=state.comment,
        duration_seconds=duration,
    )
