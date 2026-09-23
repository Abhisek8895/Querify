import streamlit as st


st.set_page_config(
    page_title="Querify",
    page_icon="🔎",
    layout="wide",
)


st.title("Querify")
st.subheader("AI-Powered SQL Assistant")

st.write(
    "Ask questions about your database in natural language "
    "and get answers using SQL."
)


st.divider()


question = st.text_area(
    "Ask your question",
    placeholder="Example: Show me the top 5 customers by total spending.",
    height=100,
)


response_format = st.radio(
    "Response format",
    ["Natural Language", "Table"],
    horizontal=True,
)


generate_button = st.button(
    "Generate",
    type="primary",
)


if generate_button:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        st.info(f"Selected response format: {response_format}")
        st.write(f"Your question: **{question}**")