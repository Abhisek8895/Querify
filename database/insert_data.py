from connection import get_connection


CUSTOMERS = [
    ("Rahul Sharma", "rahul@example.com", "Bhubaneswar"),
    ("Priya Patel", "priya@example.com", "Mumbai"),
    ("Amit Kumar", "amit@example.com", "Delhi"),
    ("Sneha Das", "sneha@example.com", "Kolkata"),
    ("Arjun Mehta", "arjun@example.com", "Bangalore"),
    ("Neha Singh", "neha@example.com", "Pune"),
    ("Rohan Gupta", "rohan@example.com", "Hyderabad"),
    ("Ananya Roy", "ananya@example.com", "Chennai"),
    ("Vikram Joshi", "vikram@example.com", "Jaipur"),
    ("Kavya Nair", "kavya@example.com", "Kochi"),
]


PRODUCTS = [
    ("Laptop", "Electronics", 75000.00),
    ("Wireless Mouse", "Accessories", 1200.00),
    ("Mechanical Keyboard", "Accessories", 4500.00),
    ("Monitor", "Electronics", 18000.00),
    ("USB-C Hub", "Accessories", 2500.00),
    ("Headphones", "Audio", 6000.00),
    ("Webcam", "Electronics", 3500.00),
    ("Smartphone", "Electronics", 45000.00),
    ("Tablet", "Electronics", 28000.00),
    ("Office Chair", "Furniture", 12000.00),
]


ORDERS = [
    (1, 1, 1, "2026-01-05"),
    (2, 2, 2, "2026-01-08"),
    (3, 3, 1, "2026-01-12"),
    (4, 4, 3, "2026-01-15"),
    (5, 5, 1, "2026-01-20"),
    (6, 6, 2, "2026-01-25"),
    (7, 7, 1, "2026-02-02"),
    (8, 8, 1, "2026-02-05"),
    (9, 9, 2, "2026-02-10"),
    (10, 10, 1, "2026-02-14"),
    (1, 4, 1, "2026-02-18"),
    (2, 6, 2, "2026-02-20"),
    (3, 8, 1, "2026-02-25"),
    (4, 10, 1, "2026-03-01"),
    (5, 3, 2, "2026-03-05"),
    (6, 5, 1, "2026-03-08"),
    (7, 7, 3, "2026-03-12"),
    (8, 9, 1, "2026-03-15"),
    (9, 2, 2, "2026-03-18"),
    (10, 1, 1, "2026-03-20"),
]


def insert_data():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.executemany(
            """
            INSERT INTO customers (name, email, city)
            VALUES (%s, %s, %s)
            """,
            CUSTOMERS,
        )

        cursor.executemany(
            """
            INSERT INTO products (name, category, price)
            VALUES (%s, %s, %s)
            """,
            PRODUCTS,
        )

        cursor.executemany(
            """
            INSERT INTO orders (customer_id, product_id, quantity, order_date)
            VALUES (%s, %s, %s, %s)
            """,
            ORDERS,
        )

        connection.commit()

        print("Sample data inserted successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    insert_data()