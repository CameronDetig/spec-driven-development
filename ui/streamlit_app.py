import os

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

    built, status_payload, status_error = _get_db_status()

    if status_error:
        st.error(status_error)
        st.stop()

    st.title("Customer FAQ Assistant")
    sub_col_1, sub_col_2 = st.columns([4, 2])
    with sub_col_1:
        st.caption("Ask questions about Mockridge Bank products and services.")
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
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg["role"] == "assistant":
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

    controls_disabled = not built
    examples = [
        "What are your checking account monthly fees?",
        "How do overdraft fees work?",
        "How do I report an unauthorized transaction?",
    ]

    if st.session_state.pending_example is not None:
        st.session_state.question_input = st.session_state.pending_example
        st.session_state.pending_example = None

    question = st.text_area(
        "Message",
        placeholder="What are your checking account monthly fees?",
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
            st.session_state.question_input = ""
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

        st.session_state.chat_messages.append({"role": "user", "content": question.strip()})
        payload = {"question": question, "top_k": top_k, "generator": generator}

        try:
            response = requests.post(f"{API_URL}/ask", json=payload, timeout=90)
            if response.status_code != 200:
                detail = response.json().get("detail", "Unknown error")
                if generator == "distilgpt2" and "setup --with-llm" in detail:
                    st.warning("LLM assets not installed. Run `python run.py setup --with-llm` first.")
                if response.status_code == 503 and "Database not built" in detail:
                    st.warning("Database is not built. Use the Build DB button above.")
                st.error(f"Request failed ({response.status_code}): {detail}")
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
            st.rerun()
        except requests.RequestException as exc:
            st.error(f"Could not reach API at {API_URL}: {exc}")


if __name__ == "__main__":
    main()
