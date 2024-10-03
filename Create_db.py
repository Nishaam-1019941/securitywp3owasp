import sqlite3

conn = sqlite3.connect('students.db')
cur = conn.cursor()


command2 = """
    CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name TEXT,
    class TEXT    ) """

cur.execute(command2)
print("Table studenten created successfully.")

# choice_text and choice_number combined is the primary key
command1 = """
    CREATE TABLE IF NOT EXISTS statements (
    statement_number INTEGER,
    choice_number INTEGER,
    choice_text TEXT,
    choice_result TEXT,
    PRIMARY KEY (statement_number, choice_number)
    ) """

cur.execute(command1)
print("Table stellingen created successfully.")

command3 = """
    CREATE TABLE IF NOT EXISTS answers (
    student_id INTEGER,
    statement_number INTEGER,
    choice_number INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (statement_number) REFERENCES statements(statement_number)
    FOREIGN KEY (choice_number) REFERENCES statements(choice_number)
    ) """

cur.execute(command3)
print("Table antwoorden created successfully.")

command4 = """
    CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    salt TEXT,
    name TEXT,
    isAdmin INTEGER
    ) """

cur.execute(command4)
print("Table users created successfully.")

conn.commit()
conn.close()
