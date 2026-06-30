import sqlite3

from src.llm import call_llm, format_history
from src.state import AgentState
from src.tools.sql_tool import SQLValidationError, execute_sql

_SCHEMA_DESCRIPTION = """
Table: products
  product_id INTEGER PRIMARY KEY
  name TEXT
  category TEXT        -- e.g. Laptops, Smartphones, TVs, Appliances, Accessories
  price REAL
  store_id INTEGER      -- foreign key -> stores.store_id

Table: stores
  store_id INTEGER PRIMARY KEY
  store_name TEXT
  city TEXT
  region TEXT

Table: sales
  sale_id INTEGER PRIMARY KEY
  product_id INTEGER    -- foreign key -> products.product_id
  sale_date TEXT         -- format YYYY-MM-DD
  quantity INTEGER
  total_amount REAL
"""


def run(state: AgentState) -> AgentState:
    message = state["message"]
    history_text = format_history(state.get("history", []))

    generated_sql = call_llm(
        f"Database schema:\n{_SCHEMA_DESCRIPTION}\n\n"
        f"User question: {message}\n\n"
        f"Write a single SQLite SELECT query (read-only) that answers this question. "
        f"Reply with ONLY the raw SQL query, no explanation, no markdown fences, no semicolon.",
        temperature=0,
    ).strip().strip("`").strip(";")

    try:
        rows = execute_sql(generated_sql)
    except SQLValidationError as e:
        answer = call_llm(
            f"The user asked: {message}\n\n"
            f"The generated SQL query was rejected for safety reasons: {e}\n\n"
            f"Explain to the user, politely and simply, that this request cannot be "
            f"processed because it would not be a safe read-only query, without showing "
            f"raw SQL errors. Answer in the same language as the user's message.",
        )
        state["response"] = answer
        return state
    except sqlite3.Error as e:
        answer = call_llm(
            f"The user asked: {message}\n\n"
            f"The generated SQL query failed with a database error: {e}\n\n"
            f"This likely means the question can't be answered with the available tables "
            f"(products, stores, sales), or the query was malformed. Explain this clearly "
            f"to the user without showing raw SQL/database errors. "
            f"Answer in the same language as the user's message.",
        )
        state["response"] = answer
        return state

    answer = call_llm(
        f"Conversation so far:\n{history_text}\n\n"
        f"User asked: {message}\n\n"
        f"SQL used: {generated_sql}\n\n"
        f"Query result (as rows): {rows}\n\n"
        f"Explain this result to the user in clear natural language. "
        f"If the result is empty, say no matching data was found. "
        f"Answer in the same language the user used.",
        system_prompt="You are a sales-data assistant for an electronics retail company.",
    )

    state["response"] = f"{answer}\n\n(SQL used: {generated_sql})"
    return state
