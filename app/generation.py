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


class FlanT5Generator:
    def __init__(self) -> None:
        self._llm = None
        self._generator = None

    def _ensure_model(self) -> None:
        if self._llm is not None or self._generator is not None:
            return

        try:
            from transformers import pipeline

            # Only download via explicit setup command; runtime should be local-only.
            # Flan-T5 is a seq2seq model designed for instruction following.
            hf_pipeline = pipeline(
                "text2text-generation",
                model="google/flan-t5-small",
                model_kwargs={"local_files_only": True},
                max_new_tokens=100,
                do_sample=False,
                num_return_sequences=1,
            )
            if _use_langchain_generation():
                from langchain_huggingface import HuggingFacePipeline

                self._llm = HuggingFacePipeline(pipeline=hf_pipeline)
            else:
                self._generator = hf_pipeline
        except Exception as exc:  # pragma: no cover - depends on local model availability
            raise RuntimeError(
                "flan-t5-small model is unavailable locally. "
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
        raw_text = str(generate_rag_answer(question=question, documents=documents, llm=self._llm)).strip()
        
        # Flan-T5 produces cleaner output than distilgpt2, but still do basic cleanup
        if raw_text:
            # Take first substantial sentence/paragraph
            first_part = raw_text.split('\n\n')[0].strip()
            
            # Basic quality check
            if self._is_low_quality_output(first_part):
                return ""
            
            return first_part
        return ""

    def _is_low_quality_output(self, text: str) -> bool:
        """Detect when LLM produces nonsensical output."""
        if not text or len(text) < 10:
            return True
        
        # Check if output is mostly punctuation or special characters
        alpha_chars = sum(c.isalpha() for c in text)
        if alpha_chars < len(text) * 0.5:  # Less than 50% letters
            return True
        
        # Check for repetitive patterns (same word repeated 3+ times)
        words = text.lower().split()
        if len(words) > 2:
            for i in range(len(words) - 2):
                if words[i] == words[i + 1] == words[i + 2]:
                    return True
        
        return False

    def _generate_legacy(self, question: str, sources: list[dict]) -> str:
        # Build context from top sources
        context_parts = [source.get("snippet", "") for source in sources[:2]]
        context = " ".join(context_parts)
        
        # Flan-T5 works better with clear instruction format
        prompt = f"Answer the question based on the context.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
        
        outputs = self._generator(prompt)
        raw_text = str(outputs[0].get("generated_text", "")).strip() if outputs else ""
        
        if raw_text:
            # Take first substantial part
            first_part = raw_text.split('\n\n')[0].strip()
            
            # Quality check
            if self._is_low_quality_output(first_part):
                return ""
            
            return first_part
        return ""

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
            # LLM produced low-quality output; fall back with explanation
            titles = ", ".join(source["title"] for source in sources[:2])
            return (
                f"Based on Mockridge Bank FAQ ({titles}), see sources below. "
                f"(Note: LLM generation was unreliable for this query. "
                f"Try 'mock' generator for consistent results.)"
            )
        return text


def get_generator(mode: str | None):
    choice = (mode or "mock").strip().lower()
    if choice == "flan-t5":
        return FlanT5Generator()
    return MockGenerator()
