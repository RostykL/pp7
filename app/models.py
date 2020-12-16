from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)

    # available_courses = db.relationship('Course', secondary=st, backref=db.backref('available_courses', lazy='dynamic'))
    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Student.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    courses = db.Column(db.String)

    # teacher_courses = db.relationship('Course', secondary=st2, backref=db.backref('teacher_courses', lazy='dynamic'))
    def __init__(self, firstname, lastname, courses):
        self.firstname = firstname
        self.lastname = lastname
        self.courses = courses

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Teacher.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    courseName = db.Column(db.String)
    author = db.Column(db.String)
    limit = db.Column(db.Integer)

    def __init__(self, courseName, author, limit):
        self.courseName = courseName
        self.author = author
        self.limit = limit

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Course.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
