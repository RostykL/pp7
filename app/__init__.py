from flask_api import FlaskAPI
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# local import
from app.models import Student, db, Teacher, Course
from instance.config import app_config
from flask import request, jsonify, abort


def create_app(config_name):
    from app.models import Student
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    migrate = Migrate(app, db)
    db.init_app(app)

    @app.route('/get', methods=['GET'])
    def test():
        rostyk = Student(
            firstname="Rostyk",
            lastname='Lukavyi',
        )
        adam = Student(
            firstname="adam",
            lastname='adaaaam',
        )
        rostyk.save()
        math_course = Course(
            courseName="Math",
            author="Christopher Bishop",
            limit=4,
        )
        math_course.save()

        ph_course = Course(
            courseName="physics",
            author="Bishop",
            limit=5,
        )
        ph_course.save()
        rostyk.available_courses.append(math_course)
        rostyk.available_courses.append(ph_course)
        adam.available_courses.append(ph_course)
        math_course.course_students.append(rostyk)
        ph_course.course_students.append(rostyk)
        ph_course.course_students.append(adam)

        courses_students_arr = []
        results = []
        for course in rostyk.available_courses:
            obj = {
                'id': course.id,
                'courseName': course.courseName,
                'author': course.author,
                'limit': course.limit,
                'students': []
            }
            for student in Course.query.filter_by(id=course.id).first().course_students:
                obj['students'].append(({"name": student.firstname, "lastname": student.lastname}))
            results.append(obj)
        response = jsonify(results)
        return response

    # @app.route('/get_course', methods=['GET'])
    # def test():
    #
    #     # results = []
    #     # for course in rostyk.available_courses:
    #     #     obj = {
    #     #         'id': course.id,
    #     #         'courseName': course.courseName,
    #     #         'author': course.author,
    #     #         'limit': course.limit
    #     #     }
    #     #     results.append(obj)
    #     response = jsonify(results)
    #     return response

    @app.route('/teachers/', methods=['POST', 'GET'])
    def create_teacher():
        if request.method == "POST":
            firstname = str(request.data.get('firstname', ''))
            lastname = str(request.data.get('lastname', ''))
            if firstname:
                teacher = Teacher(firstname=firstname, lastname=lastname)
                teacher.save()
                response = jsonify({
                    'id': teacher.id,
                    'firstname': teacher.firstname,
                    'lastname': teacher.lastname,
                })
                response.status_code = 201
                return response
        else:
            # GET
            teachers = Teacher.get_all()
            results = []

            for teacher in teachers:
                obj = {
                    'id': teacher.id,
                    'firstname': teacher.firstname,
                    'lastname': teacher.lastname,
                    'courses': []
                }

                for course in teacher.course_teachers:
                    students_arr = []
                    for std in course.course_students:
                        students_arr.append({"id": std.id, "firstname": std.firstname, "lastname": std.lastname})
                    obj['courses'].append(({"id": course.id, "limit": course.limit, "title": course.courseName, "author": course.author, "students": (students_arr)}))
                results.append(obj)

            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/teachers/<int:id>/', methods=['GET'])
    def teacher(id):
        teacher = Teacher.query.filter_by(id=id).first()
        # GET
        obj = {
            'id': teacher.id,
            'firstname': teacher.firstname,
            'lastname': teacher.lastname,
            'courses': []
        }
        for course in teacher.course_teachers:
            students_arr = []
            for std in course.course_students:
                        students_arr.append({"id": std.id, "firstname": std.firstname, "lastname": std.lastname})

            obj['courses'].append(
                ({"id": course.id, "limit": course.limit, "title": course.courseName, "author": course.author,
                  "students": students_arr}))
        response = jsonify(obj)
        response.status_code = 200
        return response

    @app.route('/teachers/<int:id>/my_courses', methods=['GET'])
    def teacher_my_courses(id):
        teacher = Teacher.query.filter_by(id=id).first()
        # GET
        obj = {
            'id': teacher.id,
            'firstname': teacher.firstname,
            'lastname': teacher.lastname,
            'courses': []
        }
        for course in teacher.course_teachers:
            students_arr = []
            for std in course.course_students:
                        students_arr.append({"id": std.id, "firstname": std.firstname, "lastname": std.lastname})

            obj['courses'].append(
                ({"id": course.id, "limit": course.limit, "title": course.courseName, "author": course.author,
                  "students": students_arr}))
        response = jsonify(obj)
        response.status_code = 200
        return response

    @app.route('/teachers/<int:id>/add_course', methods=['POST'])
    def add_course(id):
        teacher = Teacher.query.filter_by(id=id).first()
        courseName = str(request.data.get('courseName', ''))
        author = str(request.data.get('author', ''))
        limit = str(request.data.get('limit', ''))

        if courseName and author and limit:
            new_course = Course(courseName=courseName, author=author, limit=limit)
            teacher.course_teachers.append(new_course)
            teacher.save()
            new_course.save()
            response = jsonify({
                'id': new_course.id,
                'courseName': new_course.courseName,
                'author': new_course.author,
                'limit': new_course.limit,
                'students': new_course.course_students
            })
            response.status_code = 201
            return response

    @app.route('/teachers/update_course/<int:id>', methods=['PUT'])
    def update_course(id):
        course = Course.query.filter_by(id=id).first()
        courseName = str(request.data.get('courseName', ''))
        author = str(request.data.get('author', ''))
        limit = str(request.data.get('limit', ''))
        course.courseName = courseName
        course.author = author
        course.limit = limit
        course.save()

        response = jsonify({
            'updated_course': {"id": id, "name": courseName, "author": author}
        })
        response.status_code = 200
        return response

    @app.route('/teachers/delete_course/<int:id>', methods=['DELETE'])
    def delete_course(id):
        course = Course.query.filter_by(id=id).first()
        if not course:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == 'DELETE':
            course.delete()
            return {
                       "message": "Course {} deleted successfully".format(course.id)
                   }, 200

    # без request body!
    @app.route('/teachers/add_students/<int:id>/to/<int:course_id>', methods=['GET'])
    def add_student_to(id, course_id):
        course = Course.query.filter_by(id=course_id).first()
        student = Student.query.filter_by(id=id).first()
        if len(course.course_students) < int(course.limit):
            print(course, student)
            course.course_students.append(student)
            course.save()
            return {"EDDED SUCCESSFULLY": "200"}
        else:
            return {"NOOO": "4**"}
        print(id, course_id)

    @app.route('/students/', methods=['POST', 'GET'])
    def create_students():
        if request.method == "POST":
            firstname = str(request.data.get('firstname', ''))
            lastname = str(request.data.get('lastname', ''))
            if firstname:
                student = Student(firstname=firstname, lastname=lastname)
                student.save()
                response = jsonify({
                    'id': student.id,
                    'firstname': student.firstname,
                    'lastname': student.lastname,
                })
                response.status_code = 201
                return response

    return app

# @app.route('/student/<int:id>/', methods=['GET', 'PUT', 'DELETE'])
# def students_del(id):
#     # retrieve a buckelist using it's ID
#     student = Student.query.filter_by(id=id).first()
#     if not student:
#         # Raise an HTTPException with a 404 not found status code
#         abort(404)
#
#     if request.method == 'DELETE':
#         student.delete()
#         return {
#                    "message": "bucketlist {} deleted successfully".format(student.id)
#                }, 200
#
# elif request.method == 'PUT':
#     firstname = str(request.data.get('firstname', ''))
#     lastname = str(request.data.get('lastname', ''))
#     student.firstname = firstname
#     student.lastname = lastname
#     student.save()
#     response = jsonify({
#         'id': student.id,
#         'firstname': student.firstname,
#         'lastname': student.lastname
#     })
#     response.status_code = 200
#     return response
#     else:
#         # GET
#         response = jsonify({
#             'id': student.id,
#             'firstname': student.firstname,
#             'lastname': student.lastname
#         })
#         response.status_code = 200
#         return response
