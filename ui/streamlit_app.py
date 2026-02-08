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
        return bool(body.get("built", False)), body, ""
    except requests.RequestException as exc:
        return False, {}, f"Could not reach API at {API_URL}: {exc}"


def main() -> None:
    st.set_page_config(page_title="Customer FAQ Assistant", layout="centered")
    st.title("Customer FAQ Assistant")
    st.caption("Ask questions about Mockridge Bank products and services.")

    built, status_payload, status_error = _get_db_status()

    if status_error:
        st.error(status_error)
        st.stop()

    st.subheader("Vector DB Status")
    st.write(status_payload)

    if not built:
        st.warning("Database is not built yet. Build the DB to enable chat.")
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

    controls_disabled = not built
    question = st.text_area(
        "Question",
        placeholder="What are your checking account monthly fees?",
        disabled=controls_disabled,
    )
    top_k = st.slider("Top K sources", min_value=1, max_value=5, value=3, disabled=controls_disabled)
    generator = st.selectbox(
        "Generator",
        ["mock", "distilgpt2"],
        index=0,
        disabled=controls_disabled,
        help="Mock is deterministic. distilgpt2 requires LLM assets installed via run.py setup --with-llm.",
    )

    if st.button("Ask", disabled=controls_disabled):
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
            st.subheader("Answer")
            st.write(body["answer"])

            st.subheader("Retrieval")
            st.write(body["retrieval"])

            st.subheader("Sources")
            if not body["sources"]:
                st.info("No matching sources were found.")
                return

            for source in body["sources"]:
                st.markdown(f"**{source['title']}** (score: {source['score']})")
                st.write(source["snippet"])
        except requests.RequestException as exc:
            st.error(f"Could not reach API at {API_URL}: {exc}")


if __name__ == "__main__":
    main()
