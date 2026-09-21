import re


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
}


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate that the generated SQL is a safe, read-only query.

    Returns:
        tuple[bool, str]:
        - True + SQL if the query is valid
        - False + reason if the query is invalid
    """

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    sql = sql.strip()

    # Remove a trailing semicolon for statement checking.
    normalized_sql = sql.rstrip(";").strip()

    # Prevent multiple SQL statements.
    if ";" in normalized_sql:
        return False, "Multiple SQL statements are not allowed."

    # Remove SQL comments before checking keywords.
    query_without_comments = re.sub(
        r"--.*?$|/\*.*?\*/",
        "",
        normalized_sql,
        flags=re.MULTILINE | re.DOTALL,
    ).strip()

    if not query_without_comments:
        return False, "SQL query contains no executable statement."

    # Query must start with SELECT or WITH.
    if not re.match(r"^(SELECT|WITH)\b", query_without_comments, re.IGNORECASE):
        return False, "Only read-only SELECT queries are allowed."

    # Check for forbidden SQL operations.
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", query_without_comments, re.IGNORECASE):
            return False, f"Forbidden SQL operation detected: {keyword}"

    return True, sql