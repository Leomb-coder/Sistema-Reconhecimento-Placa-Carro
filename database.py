import sqlite3

def insert_plate(plate):
    conn = sqlite3.connect("plates.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT
        )
    """)

    cursor.execute("INSERT INTO plates (plate) VALUES (?)", (plate,))
    conn.commit()
    conn.close()