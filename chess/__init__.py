from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory


def main(global_config, **settings):
    my_session_factory = SignedCookieSessionFactory(
        'itsaseekreet')
    config = Configurator(settings=settings,
                          session_factory=my_session_factory)
    config.include('pyramid_chameleon')
    config.add_route('board', '/')
    config.add_route('board_data', '/board-data')
    config.add_route('move', '/move')
    config.add_route('login', '/login')
    config.add_route('loading', '/loading')
    config.add_route('check_readiness', '/check-readiness')
    config.add_static_view(name='static', path='chess:static')
    config.scan('.views')
    return config.make_wsgi_app()
