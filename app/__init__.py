import json

from flask_api import FlaskAPI
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# local import
from app.models import Student, db, Teacher, Course, CourseInvites
from instance.config import app_config
from flask import request, jsonify, abort, make_response
from flask_httpauth import HTTPBasicAuth
from functools import wraps

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if not (email and password):
        return False
    user = ''
    teacher = Teacher.query.filter_by(email=email).first()
    if (not teacher):
        user = Student.query.filter_by(email=email).first()
    else:
        user = teacher
    # print(userTest, 'hi')
    if user is None:
        return False
    if user:
        return user.password_is_valid(password)
    return False


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def bad_role(role):
    if (role == 'student'):
        return {"Access denied": "Будь ласка увійдіть як вчитель"}
    elif (role == 'teacher'):
        return {"Access denied": "Будь ласка увійдіть як студент"}


def create_app(config_name):
    from app.models import Student
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    migrate = Migrate(app, db)
    db.init_app(app)

    @app.route('/api/create_teacher/', methods=['POST'])
    def create_teacher():
        if request.method == "POST":
            firstname = str(request.data.get('firstname', ''))
            lastname = str(request.data.get('lastname', ''))
            email = str(request.data.get('email', ''))
            password = str(request.data.get('password', ''))
            username = str(request.data.get('username', ''))
            role = str(request.data.get('role', ''))
            if Teacher.query.filter_by(email=email).first() is not None:
                return {"email": "такий email вже зайнятий STATUS CODE 400"}
            if firstname and lastname and email and password:
                teacher = Teacher(firstname=firstname, lastname=lastname, email=email, password=password, role=role,
                                  username=username)
                teacher.save()
                response = jsonify({
                    'id': teacher.id,
                    'firstname': teacher.firstname,
                    'lastname': teacher.lastname,
                    'role': teacher.role
                })
                response.status_code = 201
                return response
            else:
                return {"ERROR": "Введіть всі поля firstname and lastname and email and password",
                        "STATUS CODE": 405}

    @app.route('/api/create_student/', methods=['POST'])
    def create_student():
        if request.method == "POST":
            firstname = str(request.data.get('firstname', ''))
            lastname = str(request.data.get('lastname', ''))
            email = str(request.data.get('email', ''))
            password = str(request.data.get('password', ''))
            username = str(request.data.get('username', ''))
            role = str(request.data.get('role', ''))
            if Student.query.filter_by(email=email).first() is not None:
                return {"email": "такий email вже зайнятий STATUS CODE 400"}
            if firstname and lastname and email and password:
                student = Student(firstname=firstname, lastname=lastname, email=email, password=password, role=role,
                                  username=username)
                student.save()
                response = jsonify({
                    'id': student.id,
                    'firstname': student.firstname,
                    'lastname': student.lastname,
                    'role': student.role
                })
                response.status_code = 201
                return response
            else:
                return {"ERROR": "Введіть всі поля firstname and lastname and email and password",
                        "STATUS CODE": 405}

    @app.route('/teachers/', methods=['GET'])
    def get_teacher():
        # GET
        teachers = Teacher.get_all()
        if (not teachers):
            return {"ERROR": "Немає вчителів", "STATUS CODE": 404}

        results = []
        arr = []
        for teacher in teachers:

            obj = {
                'id': teacher.id,
                'firstname': teacher.firstname,
                'lastname': teacher.lastname,
                'my_invites': [],
                'courses': []
            }
            for one in teacher.my_invites:
                arr.append({"student_id": one.student_id, "course_id": one.course_id})

            obj['my_invites'].append(arr)

            for course in teacher.course_teachers:
                students_arr = []
                for std in course.course_students:
                    students_arr.append({"id": std.id, "firstname": std.firstname, "lastname": std.lastname})
                obj['courses'].append(({"id": course.id, "limit": course.limit, "title": course.courseName,
                                        "author": course.author, "students": (students_arr)}))
            results.append(obj)

        response = jsonify(results)
        response.status_code = 200
        return response

    @app.route('/teachers/<int:id>/', methods=['GET', 'DELETE'])
    # @auth.login_required
    def teacher(id):
        if request.method == "GET":
            # email = auth.current_user()
            teacher = Teacher.query.filter_by(id=id).first()

            if not teacher:
                return {"ERROR": "Немає вчителя", "STATUS CODE": 404}

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

    @app.route('/teacher/delete_teacher/<int:id>', methods=['DELETE'])
    @auth.login_required
    def delete_teacher(id):
        teacher = Teacher.query.filter_by(id=id).first()
        email = auth.current_user()
        if not Teacher.query.filter_by(email=email).first():
            student = Student.query.filter_by(email=email).first()
            if student:
                return bad_role('student')
            return {"ERROR": "Немає даного вчителя", "STATUS CODE": 405}
        if request.method == 'DELETE':
            teacher.delete()
            return {
                       "message": "Teacher {} deleted successfully".format(teacher.id)
                   }, 200

    @app.route('/teachers/<int:id>/my_courses', methods=['GET'])
    @auth.login_required
    def teacher_my_courses(id):
        teacher = Teacher.query.filter_by(id=id).first()
        email = auth.current_user()
        if (not Teacher.query.filter_by(email=email).first()):
            student = Student.query.filter_by(email=email).first()
            if student:
                return bad_role('student')
            return {"ERROR": "Немає вчителя", "STATUS CODE": 404}

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
    @auth.login_required
    def add_course(id):
        teacher = Teacher.query.filter_by(id=id).first()
        email = auth.current_user()
        if not Teacher.query.filter_by(email=email).first():
            student = Student.query.filter_by(email=email).first()
            if student:
                return bad_role('student')
        courseName = str(request.data.get('courseName', ''))
        author = teacher.firstname
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
        else:
            return {"ERROR": "Введіть всі поля courseName and author and limit", "STATUS CODE": 405}

    @app.route('/teachers/update_course/<int:id>', methods=['PUT'])
    @auth.login_required
    def update_course(id):
        course = Course.query.filter_by(id=id).first()
        courseName = str(request.data.get('courseName', ''))
        author = str(request.data.get('author', ''))
        limit = str(request.data.get('limit', ''))
        email = auth.current_user()
        if not Teacher.query.filter_by(email=email).first():
            student = Student.query.filter_by(email=email).first()
            if student:
                return bad_role('student')
        if (not courseName and not author and not limit):
            return {"ERROR": "Введіть всі поля courseName and author and  limit", "STATUS CODE": 405}
        course.courseName = courseName
        course.author = author
        course.limit = limit
        course.save()

        response = jsonify({
            'updated_course': {"id": id, "name": courseName, "author": author, "limit": limit}
        })
        response.status_code = 200
        return response

    @app.route('/teachers/delete_course/<int:id>', methods=['DELETE'])
    @auth.login_required
    def delete_course(id):
        email = auth.current_user()
        if not Teacher.query.filter_by(email=email).first():
            student = Student.query.filter_by(email=email).first()
            if student:
                return bad_role('student')
        course = Course.query.filter_by(id=id).first()
        if not course:
            return {"ERROR": "Немає даного курсу", "STATUS CODE": 405}

        if request.method == 'DELETE':
            course.delete()
            return {
                       "message": "Course {} deleted successfully".format(course.id)
                   }, 200

    # без request body!
    @app.route('/teachers/add_students/<int:id>/to/<int:course_id>', methods=['GET'])
    @auth.login_required
    def add_student_to(id, course_id):
        email = auth.current_user()
        if not Teacher.query.filter_by(email=email).first():
            student = Student.query.filter_by(email=email).first()
            if student:
                return bad_role('student')
        course = Course.query.filter_by(id=course_id).first()
        student = Student.query.filter_by(id=id).first()
        if len(course.course_students) < int(course.limit):
            course.course_students.append(student)
            student.available_courses.append(course)
            course.save()
            return {"EDDED SUCCESSFULLY": "200"}
        else:
            return {"ERROR": "Немає місця", "limit": course.limit}

    @app.route('/students/', methods=['POST', 'GET'])
    def get_students():
        students = Student.get_all()
        email = auth.current_user()
        if not Student.query.filter_by(email=email).first():
            teacher = Teacher.query.filter_by(email=email).first()
            if teacher:
                return bad_role('teacher')
        result = []
        for student in students:
            obj = {
                "id": student.id,
                "firstname": student.firstname,
                "lastname": student.lastname,
                "username": student.username,
                "email": student.email,
                "password": student.password,
            }
            result.append(obj)

        response = jsonify(result)
        response.status_code = 200
        return response

    @app.route('/student/<int:id>', methods=['DELETE'])
    # @auth.login_required
    def delete_student(id):
        if request.method == "DELETE":
            email = auth.current_user()
        if not Student.query.filter_by(email=email).first():
            teacher = Teacher.query.filter_by(email=email).first()
            if teacher:
                return bad_role('teacher')
            student = Student.query.filter_by(id=id).first()
            if not student:
                return {"ERROR": "Немає даного студента", "STATUS CODE": 405}

            if request.method == 'DELETE':
                student.delete()
                return {
                           "message": "Student {} deleted successfully".format(student.id)
                       }, 200

    @app.route('/students/<int:student_id>/my_courses', methods=['GET'])
    @auth.login_required
    def student_courses(student_id):
        student = Student.query.filter_by(id=student_id).first()
        email = auth.current_user()
        if not Student.query.filter_by(email=email).first():
            teacher = Teacher.query.filter_by(email=email).first()
            if teacher:
                return bad_role('teacher')
            return {"ERROR": "Немає студента", "STATUS CODE": 404}

        # GET
        obj = {
            'id': student.id,
            'firstname': student.firstname,
            'lastname': student.lastname,
            'courses': []
        }
        for course in student.available_courses:
            students_arr = []
            for std in course.course_students:
                students_arr.append({"id": std.id, "firstname": std.firstname, "lastname": std.lastname})

            obj['courses'].append(
                ({"id": course.id, "limit": course.limit, "title": course.courseName, "author": course.author,
                  "students": students_arr}))
        response = jsonify(obj)
        response.status_code = 200
        return response

    @app.route('/students/request_course/', methods=['POST'])
    @auth.login_required
    def request_course():
        student_id = str(request.data.get('student_id', ''))
        course_id = str(request.data.get('course_id', ''))
        teacher_id = str(request.data.get('teacher_id', ''))
        email = auth.current_user()
        if not Student.query.filter_by(email=email).first():
            teacher = Teacher.query.filter_by(email=email).first()
            if teacher:
                return bad_role('teacher')
        if (not student_id and not course_id and not teacher_id):
            return {"ERROR": "Введіть всі поля  student_id and  course_id and  teacher_id", "STATUS CODE": "405"}

        teacher = Teacher.query.filter_by(id=teacher_id).first()
        course_invite = CourseInvites(status_accepted=False, course_id=course_id, student_id=student_id)
        teacher.my_invites.append(course_invite)
        teacher.save()
        course_invite.save()
        return jsonify([{"status_accepted": False, "course_id": course_id, "student_id": student_id}])

    @app.route('/teachers/my_invites/<int:id>', methods=['GET'])
    @auth.login_required
    def teacher_invites(id):
        teachers = [Teacher.query.filter_by(id=id).first()]
        email = auth.current_user()
        if not Teacher.query.filter_by(email=email).first():
            student = Student.query.filter_by(email=email).first()
            if student:
                return bad_role('student')
            return {"ERROR": "немає конкретного студента", "STATUS CODE": 404}

        results = []
        arr = []
        for teacher in teachers:

            obj = {
                'id': teacher.id,
                # 'firstname': teacher.firstname,
                # 'lastname': teacher.lastname,
                'my_invites': [],
                # 'courses': []
            }
            for one in teacher.my_invites:
                arr.append({"student_id": one.student_id, "course_id": one.course_id, "id": one.id,
                            "status_accepted": one.status_accepted})

            obj['my_invites'].append(arr)

            for course in teacher.course_teachers:
                students_arr = []
                for std in course.course_students:
                    students_arr.append({"id": std.id, "firstname": std.firstname, "lastname": std.lastname})
                # obj['courses'].append(({"id": course.id, "limit": course.limit, "title": course.courseName,
                #                         "author": course.author, "students": (students_arr)}))
            results.append(obj)

        response = jsonify(results)
        response.status_code = 200
        return response

    @app.route('/teacher/accept_invite/<int:id>', methods=['GET'])
    @auth.login_required
    def accept_invite(id):
        email = auth.current_user()
        if not Teacher.query.filter_by(email=email).first():
            student = Student.query.filter_by(email=email).first()
            if student:
                return bad_role('student')
        course_invite_check = CourseInvites.query.filter_by(id=id).first()
        if (not course_invite_check):
            return {"ERROR": "немає конкретного", "STATUS CODE": 404}
        course_invite_check.status_accepted = True
        this_course = Course.query.filter_by(id=course_invite_check.course_id).first()
        this_student = Student.query.filter_by(id=course_invite_check.student_id).first()
        course_invite_check.save()
        if len(this_course.course_students) < int(this_course.limit):
            this_course.course_students.append(this_student)
            this_student.available_courses.append(this_course)
            course_invite_check.delete()
            this_course.save()
            this_student.save()
            return {"EDDED SUCCESSFULLY": "200"}
        else:
            return {"ERROR": "Немає місця", "limit": this_course.limit}

    @app.route('/courses', methods=['GET'])
    def get_courses():
        courses = Course.get_all()
        result = []
        for course in courses:
            obj = {
                "id": course.id,
                "courseName": course.courseName,
                "author": course.author,
                "limit": course.limit,
            }
            result.append(obj)

        response = jsonify(result)
        response.status_code = 200
        return response

    @app.route('/courses/<int:id>', methods=['DELETE'])
    def del_course(id):
        course = Course.query.filter_by(id=id).first()
        if not course:
            return {"ERROR": "Немає даного курсу", "STATUS CODE": 405}

        if request.method == 'DELETE':
            course.delete()
            return {
                       "message": "Course {} deleted successfully".format(course.id)
                   }, 200

    return app
