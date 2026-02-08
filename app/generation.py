import os


FALLBACK_ANSWER = (
    "I could not find a confident match in Mockridge Bank FAQs. "
    "Please rephrase your question or contact support for help."
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
        self._generator = None

    def _ensure_model(self):
        if self._generator is not None:
            return

        try:
            from transformers import pipeline

            # Only download via explicit setup command; runtime should be local-only.
            self._generator = pipeline(
                "text-generation",
                model="distilgpt2",
                tokenizer="distilgpt2",
                model_kwargs={"local_files_only": True},
            )
        except Exception as exc:  # pragma: no cover - depends on local model availability
            raise RuntimeError(
                "distilgpt2 model is unavailable locally. "
                "Run `python run.py setup --with-llm` or use generator=mock."
            ) from exc

    def generate(self, question: str, sources: list[dict]) -> str:
        self._ensure_model()

        if not sources:
            return FALLBACK_ANSWER

        context = " ".join(source["snippet"] for source in sources[:2])
        prompt = f"Question: {question}\nContext: {context}\nAnswer:"

        outputs = self._generator(
            prompt,
            max_new_tokens=60,
            do_sample=False,
            num_return_sequences=1,
            pad_token_id=50256,
        )
        text = outputs[0]["generated_text"].strip()
        if not text:
            return FALLBACK_ANSWER
        return text


def get_generator(mode: str | None):
    choice = (mode or "mock").strip().lower()
    if choice == "distilgpt2":
        return DistilGPT2Generator()
    return MockGenerator()
