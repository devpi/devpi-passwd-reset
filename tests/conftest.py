from devpi_common.metadata import parse_version
from devpi_server import __version__ as _devpi_server_version
import pytest


devpi_server_version = parse_version(_devpi_server_version)


if devpi_server_version < parse_version("6.9.3dev"):
    from test_devpi_server.conftest import gentmp, httpget, makemapp  # noqa
    from test_devpi_server.conftest import makexom, mapp  # noqa
    from test_devpi_server.conftest import pypiurls, testapp, pypistage  # noqa
    from test_devpi_server.conftest import storage_info  # noqa
    from test_devpi_server.conftest import mock  # noqa
    (makexom,)  # shut up pyflakes
else:
    pytest_plugins = ["pytest_devpi_server", "test_devpi_server.plugin"]


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


if devpi_server_version < parse_version("6.9.3dev"):
    from test_devpi_server.conftest import MyTestApp

    @pytest.fixture
    def maketestapp(dummy_mailer):
        def maketestapp(xom):
            app = xom.create_app()
            app.app.registry['mailer'] = dummy_mailer
            mt = MyTestApp(app)
            mt.xom = xom
            return mt
        return maketestapp
else:
    @pytest.fixture
    def testapp(dummy_mailer, testapp):
        app = testapp.app
        while not hasattr(app, 'registry'):
            app = app.app
        app.registry['mailer'] = dummy_mailer
        return testapp
