from flask import Flask, jsonify, request, render_template
import sqlite3
from flask import jsonify
from flask_cors import CORS
# Authenticatie en Autorisatie (OWASP Top 10: A01 - Broken Access Control)
# Aangepaste code: from werkzeug.security import generate_password_hash, check_password_hash
# hashed_password = generate_password_hash(password)

# Beveiligde headers (OWASP Top 10: A06 - Security Misconfiguration)
# Aangepaste code; from flask_talisman import Talisman
# Talisman(app)


app = Flask(__name__)

# Cross-Origin Resource Sharing (CORS) (OWASP Top 10: A05 - Security Misconfiguration)
# Aangepaste code:  CORS(app, resources={r"/*": {"origins": ["https://vertrouwd-domein.com"]}})

CORS(app, resources={r"/*": {"origins": "*"}})

#statement ophalen
@app.route('/api/student/<student_nummer>/statement', methods=['GET'])
def get_statements(student_nummer):
    if not student_exists(student_nummer):
        return jsonify("Studentnummer bestaat niet"), 404
    
    next_statement_number = next_statement_number_for_student(student_nummer)

    if next_statement_number > 20:
        return jsonify("Geen stellingen meer beschikbaar"), 409
    
    statements = get_next_statement(next_statement_number)
    transformed_statement = {
        "statement_number": statements[0][0],
        "statement_choices": []
    }
    print(transformed_statement)    
    for statement in statements:
        transformed_statement["statement_choices"].append({
            "choice_number": statement[1],
            "choice_text": statement[2]
        })

    return jsonify(transformed_statement), 200

#statements opslaan
@app.route('/api/student/<student_nummer>/statement/<stelling_id>', methods=['POST'])
def save_statement_choice(student_nummer, stelling_id):
    choice = request.json.get("statement_choice")
    if choice is None:
        return jsonify("Invalid request"), 400

    
    if not statement_exists(stelling_id):
        return jsonify("Stelling bestaat niet"), 404

    
    if statement_already_saved(student_nummer, stelling_id):
        return jsonify("Stelling is al opgeslagen"), 409

    
    save_statement_choice_to_database(student_nummer, stelling_id, choice)

    result = {
        "result": "ok"
    }
    return jsonify(result), 200

def statement_exists(stelling_id):
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM statements WHERE statement_number = ?", (stelling_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_statement_choice_to_database(student_nummer, stelling_id, choice):
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("INSERT INTO answers (student_id, statement_number, choice_number) VALUES (?, ?, ?)",
              (student_nummer, stelling_id, choice))
    conn.commit()
    conn.close()

def statement_already_saved(student_nummer, stelling_id):
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM answers WHERE student_id = ? AND statement_number = ?", (student_nummer, stelling_id))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_next_statement(statement_number):
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM statements WHERE statement_number = ?", (statement_number,))
    result = c.fetchall()
    conn.close()
    return result

def student_exists(student_nummer):

    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE student_id = ?", (student_nummer,))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_student(student_nummer):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE student_id = ?", (student_nummer,))
    result = c.fetchone()
    columns = [description[0] for description in c.description]
    result = dict(zip(columns, result))
    conn.close()
    return result


def next_statement_number_for_student(student_nummer):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT MAX(statement_number) FROM answers WHERE student_id = ?", (student_nummer,))
    result = c.fetchone()
    conn.close()

    if result[0] is None:
        return 1

    return result[0] + 1

def calculate_action_type(student_nummer):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM answers WHERE student_id = ?", (student_nummer,))
    #i want athe results with their column names
    
    result = c.fetchall()
    conn.close()

    if len(result) < 20:
        return "N/A"
    
    columns = [description[0] for description in c.description]
    result = [dict(zip(columns, row)) for row in result]

    # fetch the action type for each object use the statement number and choice number
    action_types = {
        "E": 0,
        "I": 0,
        "S": 0,
        "N": 0,
        "T": 0,
        "F": 0,
        "J": 0,
        "P": 0
    }

    for row in result:
        statement_number = row["statement_number"]
        choice_number = row["choice_number"]

        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT choice_result FROM statements WHERE statement_number = ? AND choice_number = ?", (statement_number, choice_number))
        action_type = c.fetchone()[0]
        conn.close()

        action_types[action_type] += 1

    personality_type = ""
    personality_type += "E" if action_types["E"] > action_types["I"] else "I"
    personality_type += "S" if action_types["S"] > action_types["N"] else "N"
    personality_type += "T" if action_types["T"] > action_types["F"] else "F"
    personality_type += "J" if action_types["J"] > action_types["P"] else "P"

    return personality_type

@app.route('/api/student_action_type/<student_nummer>', methods=['GET'])
def get_action_type(student_nummer):
    if not student_exists(student_nummer):
        return jsonify("Studentnummer bestaat niet"), 404
    
    action_type = calculate_action_type(student_nummer)
    return jsonify(action_type), 200

# Login Register endpoint
@app.route('/register', methods=['POST'])
def register():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username_id']
    password = data['password']

    # Check if user exists in the database
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        return jsonify({'message': 'User already exists!'}), 400

    # Insert new user into the database
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User created successfully!'}), 201


# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if user exists in the database
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return jsonify({'message': 'Invalid username or password!'}), 401

    return jsonify({'message': 'Login successful!'}), 200

# login register endpoint students
@app.route('/register_student', methods=['POST'])
def register_student():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    data = request.get_json()
    student_id = data['student_id']

# Check if student exists in the database
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    if cursor.fetchone():
        return jsonify({'message': 'Student already exists!'}), 400

# Insert new student into the database
    cursor.execute('INSERT INTO students (student_id) VALUES (?, ?, ?)', (student_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Student created successfully!'}), 201

# login endpoint students
@app.route('/login_student', methods=['POST'])
def login_student():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    data = request.get_json()
    student_id = data['student_id']

    print(student_id)
    
# Check if student exists in the database
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()
    conn.close()

    if student is None:
        return jsonify({'message': 'Invalid student id or name!'}), 401

    return jsonify({'message': 'Login successful!'}), 200


# create user route 
@app.route('/api/user', methods=['POST'])
def create_user():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    data = request.get_json()
    username = data['username']
    password = data['password']
    naam = data['name']
    isAdmin = data['isAdmin']

    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        return jsonify({'message': 'User already exists!'}), 400

    
    cursor.execute('INSERT INTO users (username, password, name, isAdmin) VALUES (?, ?, ?, ?)', (username, password, naam, isAdmin))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User created successfully!'}), 201

# update user route
@app.route('/api/user/<username>', methods=['PUT'])
def update_user(username):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    data = request.get_json()
    password = data['password']
    naam = data['name']
    isAdmin = data['isAdmin']

    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user is None:
        return jsonify({'message': 'User does not exist!'}), 404

    
    cursor.execute('UPDATE users SET password = ?, name = ?, isAdmin = ? WHERE username = ?', (password, naam, isAdmin, username))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User updated successfully!'}), 200

# delete user route
@app.route('/api/user/<username>', methods=['DELETE'])
def delete_user(username):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user is None:
        return jsonify({'message': 'User does not exist!'}), 404
 
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User deleted successfully!'}), 200

# get all users route
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()

    return jsonify(users), 200

# get student
@app.route('/api/student/<student_id>', methods=['GET'])
def get_student(student_id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()
    columns = [description[0] for description in cursor.description]
    student = dict(zip(columns, student))
    conn.close()
    return jsonify(student), 200

# CRUD operations for students table

# Create a new student
@app.route('/api/student', methods=['POST'])
def create_student():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    data = request.get_json()
    student_id = data['student_id']
    name = data['name']
    student_class = data['class']
    print(data)
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    if cursor.fetchone():
        return jsonify({'message': 'Student already exists!'}), 400
        
    cursor.execute('INSERT INTO students (student_id, name, class) VALUES (?, ?, ?)', (student_id, name, student_class))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student created successfully!'}), 201

# Update an existing student
@app.route('/api/student/<student_id>', methods=['PUT'])
def update_student(student_id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    data = request.get_json()
    name = data['name']
    student_class = data['class']
        
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()
    if student is None:
        return jsonify({'message': 'Student does not exist!'}), 404
        
    cursor.execute('UPDATE students SET name = ?, class = ? WHERE student_id = ?', (name, student_class, student_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student updated successfully!'}), 200

# Delete a student
@app.route('/api/student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
        
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()
    if student is None:
        return jsonify({'message': 'Student does not exist!'}), 404
     
    cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
    conn.commit()

    # delete all answers for the student
    cursor.execute('DELETE FROM answers WHERE student_id = ?', (student_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student deleted successfully!'}), 200

# Get all students
@app.route('/api/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()

    columns = [description[0] for description in cursor.description]
    
    students = [dict(zip(columns, row)) for row in students]
    
    # add the action type to each student
    for student in students:
        student['action_type'] = calculate_action_type(student['student_id'])



    conn.close()
    return jsonify(students), 200

# Serve index.html
@app.route('/')
def HomePage():
    return app.send_static_file('index.html')

@app.route('/logged_in')
def LoggedInPage():
    return app.send_static_file('logged_in.html')

@app.route('/student_logged_in')
def StudentLoggedInPage():
    student_id = request.args.get('student_id', default=None, type=int)
    if student_id is not None:
        return render_template('student_logged_in.html')
    else:
        # Handle the case where student_id is not provided
        return "Student ID is required", 400

@app.route('/create-user')
def CreateUserPage():
    return app.send_static_file('create.html')

@app.route('/update-user/<username>')
def UpdateUserPage(username):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))

    user = cursor.fetchone()
    
    columns = [description[0] for description in cursor.description]
    user_dict = dict(zip(columns, user))
    

    return render_template('update-user.html', user=user_dict)

@app.route('/create-student')
def CreateStudentPage():
    return app.send_static_file('create_student.html')

@app.route('/update-student/<student_id>')
def UpdateStudentPage(student_id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))

    student = cursor.fetchone()
    
    columns = [description[0] for description in cursor.description]
    student_dict = dict(zip(columns, student))
    

    return render_template('update-student.html', student=student_dict)


if __name__ == '__main__':
    app.run(port=8000, debug=True) 