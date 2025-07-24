import sqlite3

DB_NAME = "users.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            user_name TEXT,
            nickname TEXT,
            game_id TEXT,
            server TEXT,
            role TEXT,
            user_type TEXT DEFAULT 'player'
        )
        """)
        
def add_user(data: dict):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users (
                telegram_id, user_name, nickname, game_id, server, role, user_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['telegram_id'],
            data['user_name'],
            data['nickname'],
            data['game_id'],
            data['server'],
            data['role'],
            data.get('user_type', 'player')
        ))

def get_user(telegram_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        if row:
            return {
                "telegram_id": row[0],
                "user_name": row[1],
                "nickname": row[2],
                "game_id": row[3],
                "server": row[4],
                "role": row[5],
                "user_type": row[6],
            }
        return None

def delete_user(telegram_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
