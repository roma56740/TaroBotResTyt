import sqlite3

DB_PATH = "bot.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Приветствие
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS greeting (
            id INTEGER PRIMARY KEY,
            photo_path TEXT,
            text TEXT
        )
    """)

    # Отзывы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            text TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Услуги
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Подарки
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------- GREETING ----------
def save_greeting(photo_path: str, text: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM greeting")
    cursor.execute("INSERT INTO greeting (photo_path, text) VALUES (?, ?)", (photo_path, text))
    conn.commit()
    conn.close()


def get_greeting():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT photo_path, text FROM greeting LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result


# ---------- REVIEWS ----------
def add_review(author: str, text: str, date_str: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reviews (author, text, date) VALUES (?, ?, ?)",
        (author, text, date_str)
    )
    conn.commit()
    conn.close()


def list_reviews(offset: int = 0, limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, author, text, date
        FROM reviews
        ORDER BY created_at DESC, id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return rows


def count_reviews():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reviews")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_review_by_id(review_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, author, text, date FROM reviews WHERE id = ?", (review_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def delete_review(review_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()


# ---------- SERVICES ----------
def add_service(name: str, description: str, file_path: str | None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO services (name, description, file_path) VALUES (?, ?, ?)",
        (name, description, file_path)
    )
    conn.commit()
    conn.close()


def list_services(offset: int = 0, limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, description, file_path
        FROM services
        ORDER BY created_at DESC, id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return rows


def count_services():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM services")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_service_by_id(service_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, file_path FROM services WHERE id = ?", (service_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def delete_service(service_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()


# ---------- GIFTS ----------
def add_gift(name: str, description: str, file_path: str | None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO gifts (name, description, file_path) VALUES (?, ?, ?)",
        (name, description, file_path)
    )
    conn.commit()
    conn.close()


def list_gifts(offset: int = 0, limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, description, file_path
        FROM gifts
        ORDER BY created_at DESC, id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return rows


def count_gifts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM gifts")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_gift_by_id(gift_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, file_path FROM gifts WHERE id = ?", (gift_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def delete_gift(gift_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gifts WHERE id = ?", (gift_id,))
    conn.commit()
    conn.close()
    