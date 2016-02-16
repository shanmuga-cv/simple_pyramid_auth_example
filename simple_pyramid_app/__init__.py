from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow,Deny, Authenticated, Everyone

from .models import (
    DBSession,
    Base,
    )

class Root:
    __acl__ = [
        (Allow, Authenticated, 'view'),
        (Deny, Authenticated, 'signup'),
        (Allow, Everyone, 'signup')
    ]

    def __init__(self, request):
        pass


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    authnpolicy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
    authzpolicy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, authentication_policy=authnpolicy, authorization_policy=authzpolicy,
                          root_factory=Root)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('student_list', '/students')
    config.add_route('add_student', '/student/add', request_method=['GET', 'POST'])
    config.add_route('student_detail', '/student/{id}')
    config.add_route('login','/login', request_method=['GET', 'POST'])
    config.add_route('logout', '/logout')

    config.scan()
    return config.make_wsgi_app()
