import sqlite3
import os

DB_DIR = os.path.expanduser("~/.recall")
DB_PATH = os.path.join(DB_DIR, "memory.db")

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS memory
                 (query TEXT NOT NULL,
                 command TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS workflows
                 (name TEXT UNIQUE NOT NULL,
                 commands TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

def save_to_memory(query: str, command: str):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO memory (query, command) VALUES (?, ?)",
            (query, command)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def search_memory(query: str) -> str | None:
    try:
        conn = get_connection()
        cursor = conn.execute(
            "SELECT command FROM memory WHERE query LIKE ? ORDER BY timestamp DESC LIMIT 1",
            (f'%{query}%',)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception:
        return None

def get_history(limit: int = 10) -> list:
    try:
        conn = get_connection()
        cursor = conn.execute(
            "SELECT query, command, timestamp FROM memory ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception:
        return []

def save_workflow(name: str, commands: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO workflows (name, commands) VALUES (?, ?)",
        (name, commands)
    )
    conn.commit()
    conn.close()

def get_workflow(name: str) -> str | None:
    conn = get_connection()
    cursor = conn.execute(
        "SELECT commands FROM workflows WHERE name=?", (name,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_workflows() -> list:
    conn = get_connection()
    cursor = conn.execute(
        "SELECT name, commands, timestamp FROM workflows ORDER BY timestamp DESC"
    )
    results = cursor.fetchall()
    conn.close()
    return results