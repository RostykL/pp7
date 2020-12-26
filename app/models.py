from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from flask_bcrypt import Bcrypt

from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()

st = db.Table('available_courses',
              db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
              db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
              )

st1 = db.Table('course_students',
               db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
               db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
               )

st2 = db.Table('course_teachers',
               db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
               db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
               )

st3 = db.Table('teacher_my_invites',
               db.Column('course_invites', db.Integer, db.ForeignKey('course_invites.id'), primary_key=True),
               db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True)
               )


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    available_courses = db.relationship('Course', secondary=st, lazy='subquery',
                                        backref=db.backref('available_courses', lazy=True))
    password = db.Column(db.String(256), nullable=False)
    email = db.Column('email', db.VARCHAR(30), nullable=False)
    role = db.Column('role', db.VARCHAR(255), nullable=False)
    username = db.Column('username', db.VARCHAR(20), nullable=False)

    def __init__(self, firstname, lastname, password, email, role, username):
        self.firstname = firstname
        self.lastname = lastname
        self.password = Bcrypt().generate_password_hash(password).decode()
        self.email = email
        self.role = role
        self.username = username

    def password_is_valid(self, password):
        return Bcrypt().check_password_hash(self.password, password)

    def get_role(self):
        return self.role

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
    course_teachers = db.relationship('Course', secondary=st2, lazy='subquery',
                                      backref=db.backref('course_teachers', lazy=True))
    my_invites = db.relationship('CourseInvites', secondary=st3, lazy='subquery',
                                 backref=db.backref('teacher_my_invites', lazy=True))
    password = db.Column(db.String(256), nullable=False)
    email = db.Column('email', db.VARCHAR(30), nullable=False)
    role = db.Column('role', db.VARCHAR(255), nullable=False)
    username = db.Column('username', db.VARCHAR(20), nullable=False)

    def __init__(self, firstname, lastname, password, email, role, username):
        self.firstname = firstname
        self.lastname = lastname
        self.password = Bcrypt().generate_password_hash(password).decode()
        self.email = email
        self.role = role
        self.username = username

    def password_is_valid(self, password):
        """
        Checks the password against it&apos;s hash to validates the user&apos;s password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def get_role(self):
        return self.role

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
    course_students = db.relationship('Student', secondary=st1, lazy='subquery',
                                      backref=db.backref('course_students', lazy=True))

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


class CourseInvites(db.Model):
    __tablename__ = 'course_invites'
    id = db.Column(db.Integer, primary_key=True)
    status_accepted = db.Column(db.Boolean)
    course_id = db.Column(db.Integer)
    student_id = db.Column(db.Integer)

    def __init__(self, status_accepted, course_id, student_id):
        self.status_accepted = status_accepted
        self.course_id = course_id
        self.student_id = student_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
