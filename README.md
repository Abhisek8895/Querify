# 🔎 Querify — AI-Powered SQL Assistant

Querify is an AI-powered SQL assistant that lets you interact with a MySQL database using natural language.

Instead of writing SQL manually, just ask questions like:

> "Show me the top 5 customers by total spending."

Querify understands the question, generates a read-only SQL query from the database schema, validates it, runs it against MySQL, and presents the result as a natural-language answer or a table.

---

## ✨ Features

- 🗣️ Ask database questions in natural language
- 🤖 AI-powered SQL generation using Groq
- 🧠 Schema-aware query generation
- 🔒 Read-only SQL validation
- 🗄️ MySQL integration
- 📊 Interactive table results
- 📈 Automatic charts for suitable results
- 💬 Natural-language answers
- ⬇️ CSV download of query results
- 💾 Conversation history during the session
- 📚 Database schema viewer in the sidebar
- ⚡ Table mode skips the second LLM call
- 🎨 Streamlit-based UI

---

## 🏗️ Architecture

```text
                    User
                      │
                      ▼
             ┌─────────────────┐
             │  Streamlit UI   │
             └────────┬────────┘
                      │  natural-language question
                      ▼
             ┌─────────────────┐
             │  SQL Generator  │  (Groq)
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  SQL Validator  │  (local)
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  MySQL Database │
             └────────┬────────┘
                      │  query results
              ┌───────┴────────┐
              ▼                ▼
       Natural Language       Table
              │                │
              ▼                ▼
    Response Generator     DataFrame
          (Groq)          + Charts
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | Web interface |
| Groq | LLM inference |
| LangChain | LLM integration and prompt handling |
| MySQL | Database |
| mysql-connector-python | MySQL connection |
| Pandas | Data processing and table display |
| python-dotenv | Environment variable management |

---

## 📁 Project Structure

```text
Querify/
│
├── app.py
│
├── ai_engine/
│   ├── __init__.py
│   ├── llm.py
│   ├── sql_generator.py
│   ├── sql_validator.py
│   └── response_generator.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── schema.py
│   ├── query_executor.py
│   ├── init_db.py
│   └── insert_data.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### Main Components

**`app.py`** — The main Streamlit application. Handles user interaction, response format selection, conversation history, the query execution flow, table visualization, charts, and CSV downloads.

**`ai_engine/llm.py`** — Initializes the Groq LLM using the API key and model configured in `.env`.

**`ai_engine/sql_generator.py`** — Converts natural-language questions into MySQL queries using the database schema. The generator is instructed to:

- Use only existing tables and columns
- Generate read-only SQL
- Use MySQL syntax
- Avoid unsupported SQL dialects
- Reject unrelated programming questions

**`ai_engine/sql_validator.py`** — Validates generated SQL locally before execution. It checks that:

- The query is not empty
- Multiple statements are not allowed
- Only `SELECT` and `WITH` queries are accepted
- Write/destructive operations are rejected

**`ai_engine/response_generator.py`** — Converts query results into a concise natural-language answer. Used only in Natural Language mode.

**`database/connection.py`** — Handles the MySQL connection.

**`database/schema.py`** — Reads the database structure and formats it for the SQL generator.

**`database/query_executor.py`** — Executes validated SQL and returns column names and rows.

**`database/init_db.py`** — Creates the required tables.

**`database/insert_data.py`** — Inserts sample customers, products, and orders.

---

## ⚙️ How It Works

Suppose the user asks: *"How many customers are in the database?"*

**1. Read the schema**

Querify retrieves the available tables and columns from MySQL:

```text
Table: customers
Columns: id, name, email, city
```

**2. Generate SQL**

The question and schema are sent to the LLM, which returns:

```sql
SELECT COUNT(*) AS customer_count
FROM customers;
```

**3. Validate SQL**

Before execution, Querify checks that the query is read-only and follows the safety rules.

**4. Execute the query**

The validated query runs against MySQL.

**5. Display the result**

*Natural Language mode:*

> There are 10 customers in the database.

*Table mode:*

```text
+----------------+
| customer_count |
+----------------+
| 10             |
+----------------+
```

---

## 🔑 API Usage

Querify minimizes unnecessary LLM calls.

**Natural Language mode — 2 LLM calls per question**

```text
User question → Groq (generate SQL) → Local validation → MySQL → Groq (generate answer)
```

**Table mode — 1 LLM call per question**

```text
User question → Groq (generate SQL) → Local validation → MySQL → DataFrame
```

SQL validation, database operations, DataFrame processing, charts, and CSV downloads do not require an LLM call.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Abhisek8895/Querify.git
cd Querify
```

### 2. Create a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ MySQL Setup

Make sure MySQL is installed and running, then create the database:

```sql
CREATE DATABASE querify;
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=querify
```

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key |
| `GROQ_MODEL` | LLM model used by Querify |
| `DB_HOST` | MySQL host |
| `DB_PORT` | MySQL port |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | Database name |

> ⚠️ Never commit your `.env` file or expose your API key publicly.

---

## 🏗️ Initialize the Database

Create the required tables:

```bash
python -m database.init_db
```

Expected output: `Tables created successfully.`

## 🌱 Insert Sample Data

Populate the database with sample customers, products, and orders:

```bash
python -m database.insert_data
```

Expected output: `Sample data inserted successfully.`

> ⚠️ `insert_data.py` inserts sample records. Don't run it repeatedly against the same database unless you want duplicate data.

---

## ▶️ Run Querify

```bash
streamlit run app.py
```

Streamlit will provide a local URL, typically <http://localhost:8501>. Open it in your browser and start asking questions.

---

## 💡 Example Questions

**Basic**
- How many customers are in the database?
- How many products are available?
- How many orders were placed?

**Customers**
- Show all customers from Mumbai.
- Which customers have placed orders?
- Show the top 5 customers by total spending.

**Products**
- Which product is the most expensive?
- Show all products in the Electronics category.
- Which product category generates the most revenue?

**Orders**
- Show orders from last month.
- How many orders were placed last month?
- Show the most recent orders.

---

## 📊 Response Modes

**Natural Language** — The query result is converted into a concise answer by the LLM.

> The database contains 10 customers.

**Table** — The raw result is shown as an interactive Pandas DataFrame, with optional charts and CSV download.

---

## 🔒 SQL Safety

Querify is designed to execute read-only queries only. The validator rejects queries containing operations such as:

`INSERT` · `UPDATE` · `DELETE` · `DROP` · `ALTER` · `TRUNCATE` · `CREATE` · `GRANT` · `REVOKE`

It also blocks multiple statements in a single generated query, and only accepts queries that begin with `SELECT` or `WITH`.

> **Note:** The validator is an application-level safety layer, not a complete database security boundary. Use database credentials with appropriately restricted (ideally read-only) permissions.

---

## 📌 Database Schema

Querify currently uses three tables:

```text
customers                products                 orders
├── id                   ├── id                   ├── id
├── name                 ├── name                 ├── customer_id  → customers.id
├── email                ├── category             ├── product_id   → products.id
└── city                 └── price                ├── quantity
                                                  └── order_date
```

---

## 🎯 Project Goals

Querify aims to make database interaction more accessible by letting people query data in plain language instead of hand-writing SQL. It also demonstrates how generative AI can be combined with a traditional database while keeping SQL validation and execution separate from the LLM.

---

## 🔮 Future Improvements

- Schema caching
- More advanced SQL validation
- Query execution limits
- Improved error handling
- Authentication
- Support for additional databases
- Persistent query history
- User-specific database connections
- More visualization options
- Streaming AI responses
- Production deployment
- Automated testing

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Test them
5. Submit a pull request

---

## 📄 License

This project is available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Abhisek Mishra**

Built with Python, Streamlit, MySQL, LangChain, and Groq.