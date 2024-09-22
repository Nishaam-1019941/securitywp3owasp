import json
import sqlite3


with open('students.json', 'r') as f:
    data = json.load(f)


conn = sqlite3.connect('students.db')


c = conn.cursor()


for student in data:
    student_class = student['student_class']
    student_name = student['student_name']
    student_number = student['student_number']

   
    c.execute("INSERT INTO students (class, name, student_id) VALUES (?, ?, ?)",
              (student_class, student_name, student_number))


conn.commit()


conn.close()