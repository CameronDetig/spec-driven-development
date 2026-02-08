from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate


RAG_PROMPT = PromptTemplate.from_template(
    (
        "Answer the customer's question about Mockridge Bank using only the provided context.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
)


def _build_context(documents: list[Document]) -> str:
    chunks: list[str] = []
    for doc in documents:
        title = str(doc.metadata.get("title", "")).strip()
        if title:
            chunks.append(f"{title}: {doc.page_content}")
        else:
            chunks.append(doc.page_content)
    return "\n\n".join(chunks).strip()


def generate_answer(question: str, documents: list[Document], llm) -> str:
    context = _build_context(documents)
    chain = RAG_PROMPT | llm | StrOutputParser()
    return chain.invoke({"question": question, "context": context})
