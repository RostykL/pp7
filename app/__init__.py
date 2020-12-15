from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from app.models import Student, db
from instance.config import app_config
from flask import request, jsonify, abort

# initialize sql-alchemy

def create_app(config_name):
    from app.models import Student
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/students/', methods=['POST', 'GET'])
    def students():
        if request.method == "POST":
            firstname = str(request.data.get('firstname', ''))
            lastname = str(request.data.get('lastname', ''))
            if firstname:
                student = Student(firstname=firstname, lastname=lastname)
                student.save()
                response = jsonify({
                    'student_id': student.student_id,
                    'firstname': student.firstname,
                    'lastname': student.lastname,
                })
                response.status_code = 201
                return response
        else:
            # GET
            students = Student.get_all()
            results = []

            for student in students:
                obj = {
                    'student_id': student.student_id,
                    'firstname': student.firstname,
                    'lastname': student.lastname,
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            print(results)
            return response

    return app
