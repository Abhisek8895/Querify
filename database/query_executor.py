from database.connection import get_connection


def execute_query(sql: str) -> dict:
    """
    Execute a SQL query and return column names and rows.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        return {
            "columns": columns,
            "rows": rows,
        }

    finally:
        cursor.close()
        connection.close()