from database.connection import get_connection


def get_schema() -> str:
    """
    Retrieve the database schema and format it as text
    for the SQL generation model.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        schema_parts = []

        for table in tables:
            table_name = table[0]

            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()

            schema_parts.append(f"Table: {table_name}")
            schema_parts.append("Columns:")

            for column in columns:
                column_name = column[0]
                column_type = column[1]

                schema_parts.append(
                    f"- {column_name} ({column_type})"
                )

            schema_parts.append("")

        return "\n".join(schema_parts).strip()

    finally:
        connection.close()