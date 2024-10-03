import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('students.db')
c = conn.cursor()

hashed_password = hash_password('admin')
c.execute("INSERT INTO users (username, password, name, isAdmin) VALUES (?, ?, ?, ?)",
          ('admin', hashed_password, 'admin', 1))

c.execute("SELECT username, password FROM users")
users = c.fetchall()

for username, password in users:
    hashed_password = hash_password(password)
    c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))

conn.commit()
conn.close()