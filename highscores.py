import sqlite3
from typing import Tuple, Optional


class HighscoreDB:
    def __init__(self, db_name: str = "highscore.db"):
        self.db_conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.connect(db_name)
        self.create_table()

    def connect(self, db_name: str) -> None:
        try:
            self.db_conn = sqlite3.connect(db_name)
            self.cursor = self.db_conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting local db: {e}")
            raise

    def create_table(self) -> None:
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS highscores (
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL
                );
            """)
            self.db_conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating highscores table: {e}")
            raise

    def highest_score(self) -> Tuple[str, int]:
        try:
            self.cursor.execute("SELECT name, score FROM highscores ORDER BY score DESC LIMIT 1;")
            return self.cursor.fetchone() or ("", 0)
        except sqlite3.Error as e:
            print(f"Error querying highest score: {e}")
            return "", 0

    def add_score(self, name: str, score: int) -> None:
        try:
            self.cursor.execute("INSERT INTO highscores (name, score) VALUES (?, ?)", (name, score))
            self.db_conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting score: {e}")
            raise

    def close(self) -> None:
        self.cursor.close()
        self.db_conn.close()
