import json
import sqlite3

# Open and read the JSON file
with open('actiontype_statements.json', 'r') as f:
    data = json.load(f)

# Connect to the SQLite database
conn = sqlite3.connect('students.db')

# Create a cursor object
c = conn.cursor()

# Iterate over the list of dictionaries
for statement in data:
    statement_number = statement['statement_number']
    for choice in statement['statement_choices']:
        choice_number = choice['choice_number']
        choice_text = choice['choice_text']
        choice_result = choice['choice_result']

        # Insert the data into the database
        c.execute("INSERT INTO statements (statement_number, choice_number, choice_text, choice_result) VALUES (?, ?, ?, ?)",
                  (statement_number, choice_number, choice_text, choice_result))

# Commit the changes
conn.commit()

# Close the database connection
conn.close()