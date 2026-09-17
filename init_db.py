import sqlite3

conn = sqlite3.connect('birthdays.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dob DATE NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        room_no TEXT,
        dob DATE
    )
''')
# conn.execute('DROP TABLE IF EXISTS birthday_requests')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS birthday_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dob DATE,
        room_no TEXT,
        proof TEXT,
        requested_by TEXT
    )
''')

# conn.execute('DROP TABLE IF EXISTS suggestions')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    suggestion_text TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

''')


conn.commit()
conn.close()

print("Database initialized successfully!")