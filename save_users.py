import sqlite3


conn = sqlite3.connect('students.db')


c = conn.cursor()

# insert a user into db
c.execute("INSERT INTO users (username, password, name, isAdmin) VALUES (?, ?, ?, ?)",
          ('admin', 'admin', 'admin', 1)) 

conn.commit()


conn.close()