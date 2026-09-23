from langchain_core.prompts import ChatPromptTemplate

from ai_engine.llm import get_llm


SYSTEM_PROMPT = """
You are the response generator for Querify, an AI-powered SQL assistant.

Your task is to convert SQL query results into a clear, concise
natural-language answer to the user's original question.

Rules:
1. Answer only using the provided query results.
2. Never invent or assume data.
3. Do not generate SQL.
4. Do not mention internal implementation details unless necessary.
5. Keep the answer concise and easy to understand.
6. If the query returned no results, clearly say that no matching data was found.
7. Preserve important numbers and values from the query results.
8. Format large numbers clearly when appropriate.
9. If the results contain multiple rows, summarize the important information
   rather than unnecessarily repeating every row.
10. Querify is a SQL/database assistant, so keep the response focused on
    the user's database question.

User question:
{question}

SQL query:
{sql}

Column names:
{columns}

Query results:
{rows}
"""


def generate_response(
    question: str,
    sql: str,
    columns: list,
    rows: list,
) -> str:
    """
    Generate a natural-language response from SQL query results.
    """

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Generate the answer to the user's question."),
        ]
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "question": question,
            "sql": sql,
            "columns": columns,
            "rows": rows,
        }
    )

    return response.content.strip()