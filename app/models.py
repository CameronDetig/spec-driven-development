from pydantic import BaseModel


class Source(BaseModel):
    id: str
    title: str
    snippet: str
    score: float


class RetrievalMeta(BaseModel):
    top_k: int
    matched: int


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    retrieval: RetrievalMeta
