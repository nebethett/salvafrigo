import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"

def execute_sql_file(cursor, file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        cursor.executescript(file.read())

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    execute_sql_file(cursor, BASE_DIR / "schema.sql")
    execute_sql_file(cursor, BASE_DIR / "seed.sql")

    conn.commit()
    conn.close()

    print("Database inizializzato correttamente.")

if __name__ == "__main__":
    init_db()