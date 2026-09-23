from database.connection import get_connection


def execute_query(sql: str):
    """
    Execute a SQL query and return the results.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(sql)

        results = cursor.fetchall()

        return results

    finally:
        cursor.close()
        connection.close()