from connection import get_connection


CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        city VARCHAR(100)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(150) NOT NULL,
        category VARCHAR(100),
        price DECIMAL(10, 2) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        order_date DATE NOT NULL,

        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """,
]


def create_tables():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        for query in CREATE_TABLES:
            cursor.execute(query)

        connection.commit()

        print("Tables created successfully.")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_tables()