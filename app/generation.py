import importlib.util


FALLBACK_ANSWER = (
    "I could not find a confident match in Mockridge Bank FAQs. "
    "Please rephrase your question or contact support for help."
)


def _use_langchain_generation() -> bool:
    return bool(importlib.util.find_spec("langchain_core")) and bool(
        importlib.util.find_spec("langchain_huggingface")
    )


class MockGenerator:
    def generate(self, question: str, sources: list[dict]) -> str:
        if not sources:
            return FALLBACK_ANSWER

        titles = ", ".join(source["title"] for source in sources[:2])
        primary = sources[0]["snippet"]
        return (
            f"Based on Mockridge Bank FAQ ({titles}): "
            f"{primary}"
        )


class DistilGPT2Generator:
    def __init__(self) -> None:
        self._llm = None
        self._generator = None

    def _ensure_model(self) -> None:
        if self._llm is not None or self._generator is not None:
            return

        try:
            from transformers import pipeline

            # Only download via explicit setup command; runtime should be local-only.
            hf_pipeline = pipeline(
                "text-generation",
                model="distilgpt2",
                tokenizer="distilgpt2",
                model_kwargs={"local_files_only": True},
                max_new_tokens=60,
                do_sample=False,
                num_return_sequences=1,
                pad_token_id=50256,
                return_full_text=False,
            )
            if _use_langchain_generation():
                from langchain_huggingface import HuggingFacePipeline

                self._llm = HuggingFacePipeline(pipeline=hf_pipeline)
            else:
                self._generator = hf_pipeline
        except Exception as exc:  # pragma: no cover - depends on local model availability
            raise RuntimeError(
                "distilgpt2 model is unavailable locally. "
                "Run `python run.py setup --with-llm` or use generator=mock."
            ) from exc

    def _generate_with_langchain(self, question: str, sources: list[dict]) -> str:
        from langchain_core.documents import Document

        from app.rag_chain import generate_answer as generate_rag_answer

        documents = [
            Document(
                page_content=str(source.get("snippet", "")),
                metadata={"title": str(source.get("title", "")), "id": str(source.get("id", ""))},
            )
            for source in sources[:3]
        ]
        return str(generate_rag_answer(question=question, documents=documents, llm=self._llm)).strip()

    def _generate_legacy(self, question: str, sources: list[dict]) -> str:
        context = " ".join(source.get("snippet", "") for source in sources[:2])
        prompt = f"Question: {question}\nContext: {context}\nAnswer:"
        outputs = self._generator(prompt)
        return str(outputs[0].get("generated_text", "")).strip() if outputs else ""

    def generate(self, question: str, sources: list[dict]) -> str:
        self._ensure_model()

        if not sources:
            return FALLBACK_ANSWER

        text = (
            self._generate_with_langchain(question=question, sources=sources)
            if self._llm is not None
            else self._generate_legacy(question=question, sources=sources)
        )
        if not text:
            return FALLBACK_ANSWER
        return text


def get_generator(mode: str | None):
    choice = (mode or "mock").strip().lower()
    if choice == "distilgpt2":
        return DistilGPT2Generator()
    return MockGenerator()
