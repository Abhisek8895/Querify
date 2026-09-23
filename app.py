import pandas as pd
import streamlit as st

from ai_engine.response_generator import generate_response
from ai_engine.sql_generator import generate_sql
from ai_engine.sql_validator import validate_sql
from database.query_executor import execute_query
from database.schema import get_schema


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
        try:
            # Step 1: Get database schema
            schema = get_schema()

            # Step 2: Generate SQL
            with st.spinner("Generating SQL..."):
                sql = generate_sql(question, schema)

            # Step 3: Validate SQL
            is_valid, validation_result = validate_sql(sql)

            if not is_valid:
                st.error(validation_result)
                st.stop()

            validated_sql = validation_result

            # Show generated SQL
            with st.expander("View generated SQL"):
                st.code(validated_sql, language="sql")

            # Step 4: Execute SQL
            with st.spinner("Executing query..."):
                result = execute_query(validated_sql)

            columns = result["columns"]
            rows = result["rows"]

            # Step 5: Handle empty results
            if not rows:
                st.info("No matching data was found.")
                st.stop()

            # Step 6: Display according to user's choice
            if response_format == "Table":

                dataframe = pd.DataFrame(
                    rows,
                    columns=columns,
                )

                st.subheader("Query Results")
                st.dataframe(
                    dataframe,
                    use_container_width=True,
                )

            else:

                with st.spinner("Generating response..."):
                    response = generate_response(
                        question=question,
                        sql=validated_sql,
                        columns=columns,
                        rows=rows,
                    )

                st.subheader("Answer")
                st.write(response)

        except Exception as error:
            st.error(
                f"Something went wrong while processing your request: {error}"
            )