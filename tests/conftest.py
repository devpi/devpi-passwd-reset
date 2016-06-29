from test_devpi_server.conftest import MyTestApp
from test_devpi_server.conftest import gentmp, httpget, makemapp  # noqa
from test_devpi_server.conftest import makexom, mapp  # noqa
from test_devpi_server.conftest import pypiurls, testapp, pypistage  # noqa
from test_devpi_server.conftest import storage_info  # noqa
from test_devpi_server.conftest import mock  # noqa
import pytest


(makexom,)  # shut up pyflakes


@pytest.fixture
def xom(makexom):
    import devpi_passwd_reset.main
    import devpi_web.main
    xom = makexom(plugins=[
        (devpi_web.main, None),
        (devpi_passwd_reset.main, None)])
    return xom


@pytest.fixture
def dummy_mailer():
    from pyramid_mailer.mailer import DummyMailer
    return DummyMailer()


@pytest.fixture
def maketestapp(dummy_mailer):
    def maketestapp(xom):
        app = xom.create_app()
        app.app.registry['mailer'] = dummy_mailer
        mt = MyTestApp(app)
        mt.xom = xom
        return mt
    return maketestapp
