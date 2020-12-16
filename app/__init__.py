from flask_api import FlaskAPI
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# local import
from app.models import Student, db, Teacher
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

    @app.route('/teachers/', methods=['POST', 'GET'])
    def create_teacher():
        if request.method == "POST":
            firstname = str(request.data.get('firstname', ''))
            lastname = str(request.data.get('lastname', ''))
            if firstname:
                teacher = Teacher(firstname=firstname, lastname=lastname, courses='[]')
                teacher.save()
                response = jsonify({
                    'id': teacher.id,
                    'firstname': teacher.firstname,
                    'lastname': teacher.lastname,
                    'courses': teacher.courses
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
                    'courses': teacher.courses
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/teachers/<int:id>/', methods=['GET'])
    def teacher(id):
        teacher = Teacher.query.filter_by(id=id).first()
        # GET
        response = jsonify({
            'id': teacher.id,
            'firstname': teacher.firstname,
            'lastname': teacher.lastname
        })
        response.status_code = 200
        return response


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
#     elif request.method == 'PUT':
#         firstname = str(request.data.get('firstname', ''))
#         lastname = str(request.data.get('lastname', ''))
#         student.firstname = firstname
#         student.lastname = lastname
#         student.save()
#         response = jsonify({
#             'id': student.id,
#             'firstname': student.firstname,
#             'lastname': student.lastname
#         })
#         response.status_code = 200
#         return response
#     else:
#         # GET
#         response = jsonify({
#             'id': student.id,
#             'firstname': student.firstname,
#             'lastname': student.lastname
#         })
#         response.status_code = 200
#         return response

    return app
