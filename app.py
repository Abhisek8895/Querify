import time

import pandas as pd
import streamlit as st

from ai_engine.response_generator import generate_response
from ai_engine.sql_generator import generate_sql
from ai_engine.sql_validator import validate_sql
from database.query_executor import execute_query
from database.schema import get_schema


# ---------- Page config ----------
st.set_page_config(
    page_title="Querify",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- CSS ----------
st.markdown(
    """
    <style>
        /* Clear Streamlit's fixed header so the title never gets cut off */
        .block-container {
            padding-top: 4.5rem;
            padding-bottom: 6rem;
            max-width: 1000px;
        }

        [data-testid="stToolbar"] {
            display: none;
        }

        footer {
            visibility: hidden;
        }

        .hero {
            text-align: center;
            padding: 1.2rem 0 0.4rem 0;
        }

        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.2;
            padding-bottom: 0.25rem;
            margin: 0;
            background: linear-gradient(90deg, #818cf8, #22d3ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-sub {
            color: #8b8fa3;
            font-size: 1.05rem;
            margin-top: 0.3rem;
        }

        .pill {
            display: inline-block;
            padding: 0.15rem 0.7rem;
            border-radius: 999px;
            font-size: 0.78rem;
            margin-right: 0.4rem;
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.35);
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 500;
        }

        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 0.6rem 0.9rem;
            border-radius: 12px;
        }

        [data-testid="stChatMessage"] {
            border-radius: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Constants & session state ----------

EXAMPLES = [
    "Show me the top 5 customers by total spending.",
    "How many orders were placed last month?",
    "Which product category earns the most revenue?",
]


if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending" not in st.session_state:
    st.session_state.pending = None


def queue_question(question: str):
    st.session_state.pending = question


# ---------- Helpers ----------

def to_dataframe(rows, columns) -> pd.DataFrame:
    """
    Convert database rows into a pandas DataFrame.

    Attempts to convert numeric-looking object columns into
    numeric types so charts work correctly.
    """

    dataframe = pd.DataFrame(
        rows,
        columns=columns,
    )

    for column in dataframe.columns:
        if dataframe[column].dtype == "object":
            try:
                dataframe[column] = pd.to_numeric(
                    dataframe[column]
                )
            except (ValueError, TypeError):
                pass

    return dataframe


def chart_spec(dataframe: pd.DataFrame):
    """
    Determine whether the query result is suitable for a chart.

    Returns:
        tuple:
            (x-axis column, numeric columns)
        or None if a chart is not appropriate.
    """

    numeric_columns = dataframe.select_dtypes(
        "number"
    ).columns.tolist()

    other_columns = [
        column
        for column in dataframe.columns
        if column not in numeric_columns
    ]

    if (
        2 <= len(dataframe) <= 50
        and numeric_columns
        and other_columns
    ):
        return other_columns[0], numeric_columns

    return None


# ---------- Query pipeline ----------

def run_pipeline(question: str, response_format: str) -> dict:
    """
    Run the complete Querify pipeline.

    Flow:
        Question
        ↓
        Schema
        ↓
        SQL Generation
        ↓
        SQL Validation
        ↓
        Query Execution
        ↓
        Natural Language / Table
    """

    message = {
        "question": question,
        "response_format": response_format,
        "error": None,
        "sql": None,
        "df": None,
        "answer": None,
        "elapsed": 0.0,
    }

    start = time.perf_counter()

    with st.status(
        "Thinking...",
        expanded=True,
    ) as status:

        try:
            # Step 1: Read database schema
            status.update(
                label="Reading database schema..."
            )

            schema = get_schema()

            if not schema.strip():
                message["error"] = (
                    "No database tables were found."
                )

                status.update(
                    label="Database schema is empty",
                    state="error",
                    expanded=False,
                )

                return message

            # Step 2: Generate SQL
            status.update(
                label="Generating SQL..."
            )

            sql = generate_sql(
                question,
                schema,
            )

            # Step 3: Validate SQL
            status.update(
                label="Validating SQL..."
            )

            is_valid, validation_result = validate_sql(
                sql
            )

            if not is_valid:
                message["error"] = validation_result

                status.update(
                    label="Validation failed",
                    state="error",
                    expanded=False,
                )

                return message

            message["sql"] = validation_result

            # Step 4: Execute SQL
            status.update(
                label="Executing query..."
            )

            result = execute_query(
                message["sql"]
            )

            columns = result["columns"]
            rows = result["rows"]

            message["df"] = to_dataframe(
                rows,
                columns,
            )

            # Step 5: Generate natural-language response
            #
            # Only Natural Language mode makes the second
            # LLM call. Table mode directly displays results.
            if (
                rows
                and response_format == "Natural Language"
            ):
                status.update(
                    label="Writing answer..."
                )

                message["answer"] = generate_response(
                    question=question,
                    sql=message["sql"],
                    columns=columns,
                    rows=rows,
                )

            # Step 6: Finish
            message["elapsed"] = (
                time.perf_counter() - start
            )

            status.update(
                label=f"Done in {message['elapsed']:.1f}s",
                state="complete",
                expanded=False,
            )

        except Exception as error:
            message["error"] = (
                "Something went wrong while processing "
                f"your request: {error}"
            )

            status.update(
                label="Error",
                state="error",
                expanded=False,
            )

    return message


# ---------- Render assistant response ----------

def render_assistant(message: dict, index: int):
    """
    Render a previous assistant response.

    Natural Language mode:
        - Main answer
        - Optional table
        - SQL

    Table mode:
        - Main table
        - Optional chart
        - SQL
    """

    # ---------- Error ----------
    if message["error"]:
        st.error(message["error"])

        if message["sql"]:
            with st.expander("🧾 Generated SQL"):
                st.code(
                    message["sql"],
                    language="sql",
                )

        return

    dataframe = message["df"]

    # ---------- Empty results ----------
    if dataframe is None or dataframe.empty:
        st.info("No matching data was found.")

        if message["sql"]:
            with st.expander("🧾 Generated SQL"):
                st.code(
                    message["sql"],
                    language="sql",
                )

        return

    # ---------- Result information ----------
    st.markdown(
        f'<span class="pill">{len(dataframe)} rows</span>'
        f'<span class="pill">{len(dataframe.columns)} columns</span>'
        f'<span class="pill">{message["elapsed"]:.1f}s</span>',
        unsafe_allow_html=True,
    )

    # ==================================================
    # Natural Language mode
    # ==================================================

    if message["response_format"] == "Natural Language":

        st.markdown("### 💬 Answer")

        st.markdown(
            message["answer"]
        )

    # ==================================================
    # Table mode
    # ==================================================

    else:

        st.markdown("### 📋 Query Results")

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Download CSV",
            data=dataframe.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="querify_results.csv",
            mime="text/csv",
            key=f"dl_{index}",
        )

        # ---------- Chart ----------
        specification = chart_spec(
            dataframe
        )

        if specification:

            st.markdown("### 📊 Chart")

            x_axis, y_columns = specification

            chart_type = st.radio(
                "Chart type",
                ["Bar", "Line"],
                horizontal=True,
                key=f"chart_type_{index}",
            )

            if chart_type == "Bar":

                st.bar_chart(
                    dataframe,
                    x=x_axis,
                    y=y_columns,
                )

            else:

                st.line_chart(
                    dataframe,
                    x=x_axis,
                    y=y_columns,
                )

    # ---------- SQL ----------
    with st.expander("🧾 Generated SQL"):

        st.code(
            message["sql"],
            language="sql",
        )


# ---------- Sidebar ----------

with st.sidebar:

    st.markdown("## 🔎 Querify")

    st.caption(
        "Ask your database anything, in plain English."
    )

    st.divider()

    # Only two output modes.
    response_format = st.radio(
        "Response format",
        ["Natural Language", "Table"],
        index=0,
        help=(
            "Table mode skips the extra LLM call "
            "for a written answer."
        ),
    )

    st.divider()

    # ---------- Database schema ----------
    with st.expander("📚 Database schema"):

        try:

            schema = get_schema()

            if schema.strip():
                st.code(
                    schema,
                    language="sql",
                )
            else:
                st.info(
                    "No database tables found."
                )

        except Exception as error:

            st.warning(
                f"Could not load schema: {error}"
            )

    st.divider()

    # ---------- Clear conversation ----------
    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# ---------- Header ----------

# ---------- Header ----------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Querify</div>
        <div class="hero-sub">
            AI-powered SQL assistant.
            Ask in natural language,
            get answers from your data.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Empty state with example cards ----------

if not st.session_state.messages:

    st.write("")

    st.markdown("##### Try one of these")

    columns = st.columns(
        len(EXAMPLES)
    )

    for column, example in zip(
        columns,
        EXAMPLES,
    ):

        with column:

            st.button(
                example,
                key=f"example_{example}",
                on_click=queue_question,
                args=(example,),
                use_container_width=True,
            )


# ---------- Conversation history ----------

for index, message in enumerate(
    st.session_state.messages
):

    with st.chat_message("user"):
        st.write(
            message["question"]
        )

    with st.chat_message("assistant"):
        render_assistant(
            message,
            index,
        )


# ---------- Chat input ----------

prompt = st.chat_input(
    "Ask a question about your data..."
)


# Handle example question clicks.
if st.session_state.pending:

    prompt = st.session_state.pending

    st.session_state.pending = None


# ---------- Process new question ----------

if prompt and prompt.strip():

    cleaned_prompt = prompt.strip()

    with st.chat_message("user"):
        st.write(cleaned_prompt)

    with st.chat_message("assistant"):

        new_message = run_pipeline(
            cleaned_prompt,
            response_format,
        )

        render_assistant(
            new_message,
            len(st.session_state.messages),
        )

    st.session_state.messages.append(
        new_message
    )

    st.rerun()