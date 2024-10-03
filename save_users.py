import sqlite3
import hashlib
import os

def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

def generate_salt():
    return os.urandom(16).hex()

conn = sqlite3.connect('students.db')
c = conn.cursor()

salt = generate_salt()
hashed_password = hash_password('admin', salt)
c.execute("INSERT INTO users (username, password, salt, name, isAdmin) VALUES (?, ?, ?, ?, ?)",
          ('admin', hashed_password, salt, 'admin', 1))

c.execute("SELECT username, password, salt FROM users")
users = c.fetchall()

for username, password, salt in users:
    hashed_password = hash_password(password, salt)
    c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))

conn.commit()
conn.close()