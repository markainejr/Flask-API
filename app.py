from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

# Student Class/Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentName = db.Column(db.String(200), unique=True)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(1))
    course = db.Column(db.String(200))

    def __init__(self, studentName, age, sex, course):
        self.studentName = studentName
        self.age = age
        self.sex = sex
        self.course = course

# Student schema
class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        fields = ("id", "studentName", "age", "sex", "course")

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

# Create a Student
@app.route('/student', methods=['POST'])
def add_student():
    try:
        studentName = request.json['studentName']
        age = request.json['age']
        sex = request.json['sex']
        course = request.json['course']

        new_student = Student(studentName=studentName, age=age, sex=sex, course=course)
        db.session.add(new_student)
        db.session.commit()

        return student_schema.jsonify(new_student), 201
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400

# Get All Students
@app.route('/student', methods=['GET'])
def get_students():
    all_students = Student.query.all()
    result = students_schema.dump(all_students)
    return jsonify(result)

# Get a Single student
@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get(id)
    if student:
        return student_schema.jsonify(student)
    return jsonify({"message": "Student not found"}), 404

# Update a Student
@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    try:
        # Retrieve the student from the database
        student = Student.query.get(id)
        if not student:
            return jsonify({"message": "Student not found"}), 404
        
        # Extract data from the request JSON
        data = request.json
        studentName = data.get('studentName')
        age = data.get('age')
        sex = data.get('sex')
        course = data.get('course')

        # Check for missing required fields
        if not studentName or not age or sex is None or course is None:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Update student information
        student.studentName = studentName
        student.age = age
        student.sex = sex
        student.course = course

        # Commit changes to the Database
        db.session.commit()

        # Return updated student information
        return student_schema.jsonify(student), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"error": str(e)}), 500
    
#Delete a student
@app.route ('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()
    if student:
        return student_schema.jsonify(student)
    return jsonify({"message": "Student not found"}), 404    
    

# Run Server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
