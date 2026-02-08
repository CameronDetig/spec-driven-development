from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.generation import get_generator
from app.models import AskResponse
from app.retrieval import build_db, get_db_status, retrieve, to_source_payload


app = FastAPI(title="Customer FAQ Assistant API")


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=400, detail=detail)


def _validate_question(payload: dict) -> str:
    if "question" not in payload:
        raise _bad_request("question is required")

    question = payload.get("question")
    if not isinstance(question, str):
        raise _bad_request("question must be a string")

    stripped = question.strip()
    if len(stripped) < 5:
        raise _bad_request("question must be at least 5 characters")
    if len(stripped) > 300:
        raise _bad_request("question must be at most 300 characters")
    return stripped


def _validate_top_k(payload: dict) -> int:
    if "top_k" not in payload:
        return 3

    top_k = payload.get("top_k")
    if top_k is None:
        raise _bad_request("top_k cannot be null")
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise _bad_request("top_k must be an integer")
    if top_k < 1 or top_k > 5:
        raise _bad_request("top_k must be between 1 and 5")
    return top_k


def _validate_generator(payload: dict) -> str:
    if "generator" not in payload:
        return "mock"

    value = payload.get("generator")
    if value is None:
        raise _bad_request("generator cannot be null")
    if not isinstance(value, str):
        raise _bad_request("generator must be a string")
    choice = value.strip().lower()
    if choice not in {"mock", "flan-t5"}:
        raise _bad_request("generator must be mock or flan-t5")
    return choice


@app.exception_handler(HTTPException)
def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: dict = Body(...)):
    if payload is None or not isinstance(payload, dict):
        raise _bad_request("request body must be a JSON object")

    question = _validate_question(payload)
    top_k = _validate_top_k(payload)
    generator_mode = _validate_generator(payload)

    db_status = get_db_status()
    if not db_status["built"]:
        raise HTTPException(status_code=503, detail="Database not built. Run POST /db/build first.")

    matched_docs = retrieve(question=question, top_k=top_k)
    sources = to_source_payload(matched_docs)

    try:
        generator = get_generator(generator_mode)
        answer = generator.generate(question=question, sources=sources)
    except RuntimeError as exc:
        # LLM generator may fail when model assets are not installed locally.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    response = {
        "answer": answer,
        "sources": sources,
        "retrieval": {
            "top_k": top_k,
            "matched": len(sources),
        },
    }
    return response


@app.get("/db/status")
def db_status():
    return get_db_status()


@app.post("/db/build")
def db_build():
    return build_db()
