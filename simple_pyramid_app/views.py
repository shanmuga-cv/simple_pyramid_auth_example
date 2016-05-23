from pyramid.security import remember, forget
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


@view_config(route_name='home')
def home_view(request):
    html = render("templates/home.jinja2", {'authenticated_student_id': request.authenticated_userid})
    return Response(html)

@view_config(route_name="student_list", permission='view')
def students_view(request):
    students = DBSession.query(Student).all()
    html = render("templates/student_list.jinja2", {'all_students':students, 'authenticated_student_id': request.authenticated_userid})
    return Response(html)

@view_config(route_name='student_detail', permission='view')
def student_detail_view(request):
    id = request.matchdict['id']
    student = DBSession.query(Student).filter(Student.id==int(id)).one_or_none()
    html = render("templates/student_details.jinja2", {'student': student, 'authenticated_student_id': request.authenticated_userid})
    status = 200 if student is not None else 400
    return Response(html, status=status)

@view_config(route_name="add_student", request_method="GET", permission='signup')
def add_student_view(request):
    html = render("templates/add_student.jinja2", {'authenticated_student_id': request.authenticated_userid})
    return Response(html)


@view_config(route_name="add_student", request_method="POST", permission='signup')
def persist_student(request):
    student_name = request.POST['student_name']
    student_gender = request.POST['student_gender']
    pwd = request.POST['pwd']
    student = Student(name=student_name, gender=student_gender, password=pwd)
    with transaction.manager:
        DBSession.add(student)
        transaction.commit()
    return HTTPFound(request.route_url('home'))

@view_config(route_name='login', request_method='GET')
def login_view(request):
    html = render('templates/login.jinja2', {'authenticated_student_id': request.authenticated_userid})
    return Response(html)

@view_config(route_name='login', request_method='POST')
def authenticate(request):
    student_name = request.POST['student_name']
    pwd = request.POST['pwd']
    student = DBSession.query(Student).filter(Student.name==student_name and Student.password==pwd).one_or_none()
    if student is not None:
        id_str = str(student.id)
        headers = remember(request, id_str)
        html = render("templates/home.jinja2", {'authenticated_student_id': id_str})
        return Response(body=html, headers=headers)

    else:
        html = render('templates/login.jinja2', {'authenticated_student_id': request.authenticated_userid})
        return Response(html)


@view_config(route_name='logout')
def logout(request):
    header = forget(request)
    html = render('templates/login.jinja2', {'authenticated_student_id': None})
    return Response(html, headers=header)
