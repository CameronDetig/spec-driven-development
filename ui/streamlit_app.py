import os
from html import escape

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def _get_db_status() -> tuple[bool, dict, str]:
    try:
        response = requests.get(f"{API_URL}/db/status", timeout=20)
        if response.status_code != 200:
            return False, {}, f"DB status request failed ({response.status_code})."
        body = response.json()
        minimal = {
            "built": bool(body.get("built", False)),
            "doc_count": int(body.get("doc_count", 0)),
        }
        return bool(body.get("built", False)), minimal, ""
    except requests.RequestException as exc:
        return False, {}, f"Could not reach API at {API_URL}: {exc}"


def main() -> None:
    st.set_page_config(page_title="Customer FAQ Assistant", layout="centered")
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
            [data-testid="stHeader"] {
                height: 0rem;
            }
            .chat-row {
                display: flex;
                margin: 0.35rem 0;
            }
            .chat-row.user {
                justify-content: flex-end;
            }
            .chat-row.assistant {
                justify-content: flex-start;
            }
            .chat-bubble {
                max-width: 78%;
                padding: 0.6rem 0.8rem;
                border-radius: 0.9rem;
                line-height: 1.35;
                word-wrap: break-word;
                color: #111111;
            }
            .chat-row.user .chat-bubble {
                background: #d8ebff;
                border-bottom-right-radius: 0.25rem;
            }
            .chat-row.assistant .chat-bubble {
                background: #f2f3f5;
                border-bottom-left-radius: 0.25rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Welcome to the Customer FAQ Assistant. Enter a question to get started.",
                "retrieval": None,
                "sources": [],
            }
        ]
    if "question_input" not in st.session_state:
        st.session_state.question_input = ""
    if "pending_example" not in st.session_state:
        st.session_state.pending_example = None
    if "pending_submission" not in st.session_state:
        st.session_state.pending_submission = None
    if "clear_question_input" not in st.session_state:
        st.session_state.clear_question_input = False

    built, status_payload, status_error = _get_db_status()

    if status_error:
        st.error(status_error)
        st.stop()

    st.title("Customer FAQ Assistant")
    sub_col_1, sub_col_2 = st.columns([4, 2])
    with sub_col_1:
        st.caption("Ask questions about Mockridge Bank's fictional products and services.")
    with sub_col_2:
        status_label = "Ready" if built else "Not Built"
        st.caption(f"DB: {status_label} | docs: {status_payload.get('doc_count', 0)}")

    if not built:
        st.warning("Retrieval database is not built yet. Press the button below to enable chat.")
        if st.button("Build DB"):
            try:
                response = requests.post(f"{API_URL}/db/build", timeout=120)
                if response.status_code != 200:
                    detail = response.json().get("detail", "Unknown error")
                    st.error(f"Build failed ({response.status_code}): {detail}")
                    st.stop()
                st.success("Database built successfully. You can now ask questions.")
                st.rerun()
            except requests.RequestException as exc:
                st.error(f"Could not build DB at {API_URL}: {exc}")
                st.stop()

    chat_window = st.container(height=420, border=True)
    with chat_window:
        for msg in st.session_state.chat_messages:
            role = "user" if msg.get("role") == "user" else "assistant"
            st.markdown(
                f"<div class='chat-row {role}'><div class='chat-bubble'>{escape(str(msg.get('content', '')))}</div></div>",
                unsafe_allow_html=True,
            )
            if role == "assistant":
                retrieval = msg.get("retrieval")
                sources = msg.get("sources", [])
                if retrieval:
                    with st.expander("Retrieval Details"):
                        st.write(retrieval)
                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            st.markdown(f"**{source['title']}** (score: {source['score']})")
                            st.write(source["snippet"])

    controls_disabled = (not built) or (st.session_state.pending_submission is not None)
    examples = [
        "What are your checking account monthly fees?",
        "How do overdraft fees work?",
        "What can I do with the mobile app?",
    ]

    if st.session_state.pending_example is not None:
        st.session_state.question_input = st.session_state.pending_example
        st.session_state.pending_example = None
    if st.session_state.clear_question_input:
        st.session_state.question_input = ""
        st.session_state.clear_question_input = False

    question = st.text_area(
        "Message",
        placeholder="Enter your question here",
        key="question_input",
        disabled=controls_disabled,
    )
    action_col_1, action_col_2 = st.columns(2)
    has_user_messages = any(msg.get("role") == "user" for msg in st.session_state.chat_messages)
    with action_col_1:
        if has_user_messages and st.button("Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "Welcome to the Customer FAQ Assistant. Enter a question to get started.",
                    "retrieval": None,
                    "sources": [],
                }
            ]
            st.session_state.clear_question_input = True
            st.session_state.pending_submission = None
            st.rerun()
    with action_col_2:
        button_col_1, button_col_2 = st.columns([3, 1])
        with button_col_1:
            st.write("")
        with button_col_2:
            submit_clicked = st.button("Submit", key="submit_btn", disabled=controls_disabled)

    st.caption("Try an example:")
    chip_cols = st.columns(3)
    for idx, example in enumerate(examples):
        with chip_cols[idx]:
            if st.button(example, key=f"example_{idx}", disabled=controls_disabled):
                st.session_state.pending_example = example
                st.rerun()
    control_col_1, control_col_2 = st.columns(2)
    with control_col_1:
        top_k = st.slider("Number of sources to retrieve", min_value=1, max_value=5, value=3, disabled=controls_disabled)
    with control_col_2:
        generator = st.selectbox(
            "Response generator type",
            ["mock", "distilgpt2"],
            index=0,
            disabled=controls_disabled,
            help="Mock is deterministic, intended for testing. distilgpt2 is an actual LLM that first needs to be installed via 'run.py setup --with-llm'",
        )

    if submit_clicked:
        if not question.strip():
            st.warning("Please enter a question before submitting.")
            return

        user_question = question.strip()
        st.session_state.chat_messages.append({"role": "user", "content": user_question})
        st.session_state.clear_question_input = True
        st.session_state.pending_submission = {
            "question": user_question,
            "top_k": top_k,
            "generator": generator,
        }
        st.rerun()

    pending_submission = st.session_state.pending_submission
    if pending_submission is not None:
        try:
            with st.spinner("Processing your question..."):
                response = requests.post(f"{API_URL}/ask", json=pending_submission, timeout=90)
                if response.status_code != 200:
                    detail = response.json().get("detail", "Unknown error")
                    if pending_submission["generator"] == "distilgpt2" and "setup --with-llm" in detail:
                        st.warning("LLM assets not installed. Run `python run.py setup --with-llm` first.")
                    if response.status_code == 503 and "Database not built" in detail:
                        st.warning("Database is not built. Use the Build DB button above.")
                    st.error(f"Request failed ({response.status_code}): {detail}")
                    st.session_state.pending_submission = None
                    return

                body = response.json()
                st.session_state.chat_messages.append(
                    {
                        "role": "assistant",
                        "content": body["answer"],
                        "retrieval": body.get("retrieval"),
                        "sources": body.get("sources", []),
                    }
                )
            st.session_state.pending_submission = None
            st.rerun()
        except requests.RequestException as exc:
            st.session_state.pending_submission = None
            st.error(f"Could not reach API at {API_URL}: {exc}")


if __name__ == "__main__":
    main()
