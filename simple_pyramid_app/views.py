from pyramid.httpexceptions import HTTPFound
import transaction
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Student,
    )


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home_view(request):
    html = render("templates/home.jinja2", {})
    return Response(html)

@view_config(route_name="student_list")
def students_view(request):
    students = DBSession.query(Student).all()
    html = render("templates/student_list.jinja2", {'all_students':students})
    return Response(html)

@view_config(route_name='student_detail')
def student_detail_view(request):
    id = request.matchdict['id']
    student = DBSession.query(Student).filter(Student.id==int(id)).one_or_none()
    html = render("templates/student_details.jinja2", {'student': student})
    status = 200 if student is not None else 400
    return Response(html, status=status)

@view_config(route_name="add_student", request_method="GET")
def add_student_view(request):
    html = render("templates/add_student.jinja2", {})
    return Response(html)


@view_config(route_name="add_student", request_method="POST")
def persist_student(request):
    student_name = request.POST['student_name']
    student_gender = request.POST['student_gender']
    student = Student(name=student_name, gender=student_gender)
    with transaction.manager:
        DBSession.add(student)
        transaction.commit()
    return HTTPFound(request.route_url('home'))