from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import ReviewRequest, ReviewResponse
from app.services.review_service import review_pull_request

app = FastAPI(title="PR Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/api/v1/review", response_model=ReviewResponse, summary="Review Pull Request")
async def review(payload: ReviewRequest) -> ReviewResponse:
    return review_pull_request(payload)
