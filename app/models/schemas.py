from pydantic import BaseModel, Field, ConfigDict


class ReviewRequest(BaseModel):
    pr: int
    repo: str
    title: str
    desc: str | None = None
    author: str
    base_branch: str = "main"
    head_branch: str
    raw_diff: str
    n8n_callback_url: str | None = None


class ReviewResponse(BaseModel):
    run_id: str
    pr: int
    decision: str
    severity: str
    score: float
    github_review_id: int | None = None
    comment: str
    duration_seconds: float


class ReviewState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    run_id: str
    pr: int
    repo: str
    title: str
    desc: str
    raw_diff: str
    files: list[dict] = Field(default_factory=list)
    chunks: list[dict] = Field(default_factory=list)
    security: list[dict] = Field(default_factory=list)
    severity: str = "none"
    style: list[dict] = Field(default_factory=list)
    score: float = 100.0
    refactor: list[dict] = Field(default_factory=list)
    decision: str = "comment"
    comment: str = ""
    github_review_id: int | None = None
    parse_error: bool = False
