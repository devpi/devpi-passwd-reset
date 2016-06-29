import bs4
import pytest


def test_importable():
    import devpi_passwd_reset
    assert devpi_passwd_reset.__version__


def request_link(testapp, **params):
    r = testapp.xget(
        200, 'http://localhost/+password-reset',
        headers=dict(accept="text/html"))
    r = testapp.post(
        'http://localhost/+password-reset',
        code=200,
        params=dict({'submit': 'Send link'}, **params),
        headers=dict(accept="text/html"))
    return r


@pytest.mark.parametrize("name", ["foo", "foo@example.com"])
def test_reset(dummy_mailer, mapp, name, testapp):
    mapp.create_user("foo", password="foo", email="foo@example.com")
    r = request_link(testapp, user_or_email=name)
    (_, msg) = r.html.select('#content p')
    assert msg.text == 'A mail with a link to reset your password has been sent.'
    (msg,) = dummy_mailer.outbox
    assert msg.send_to == {"foo@example.com"}
    html = bs4.BeautifulSoup(msg.html, "html5lib")
    (link,) = html.select('a')
    assert link.attrs['href'] in msg.body
    r = testapp.xget(
        200, link.attrs['href'],
        headers=dict(accept="text/html"))
    header = r.html.select('h1')[-1]
    assert header.text == 'Set new password for user foo'
    r = testapp.post(
        link.attrs['href'],
        code=200,
        params={
            'password': 'bar',
            'password2': 'bar',
            'submit': 'Set new password'},
        headers=dict(accept="text/html"))
    (msg,) = r.html.select('#content p')
    assert msg.text == 'You successfully changed your password.'
    mapp.login("foo", "foo", code=401)
    mapp.login("foo", "bar")


def test_empty_password(dummy_mailer, mapp, testapp):
    mapp.create_user("foo", password="foo", email="foo@example.com")
    r = request_link(testapp, user_or_email='foo')
    (msg,) = dummy_mailer.outbox
    html = bs4.BeautifulSoup(msg.html, "html5lib")
    (link,) = html.select('a')
    r = testapp.post(
        link.attrs['href'],
        code=200,
        params={
            'password': '',
            'password2': '',
            'submit': 'Set new password'},
        headers=dict(accept="text/html"))
    (error,) = r.html.select('.error')
    assert error.text == "Error: The password can't be empty."


def test_password_mismatch(dummy_mailer, mapp, testapp):
    mapp.create_user("foo", password="foo", email="foo@example.com")
    r = request_link(testapp, user_or_email='foo')
    (msg,) = dummy_mailer.outbox
    html = bs4.BeautifulSoup(msg.html, "html5lib")
    (link,) = html.select('a')
    r = testapp.post(
        link.attrs['href'],
        code=200,
        params={
            'password': 'foo',
            'password2': 'bar',
            'submit': 'Set new password'},
        headers=dict(accept="text/html"))
    (error,) = r.html.select('.error')
    assert error.text == "Error: The entered passwords don't match."


def test_invalid_user(mapp, testapp):
    r = request_link(testapp, user_or_email='foo')
    (error,) = r.html.select('.error')
    assert error.text == 'Error: No user with that name or email.'
    (user_or_email,) = r.html.select('[name=user_or_email]')
    assert user_or_email.attrs['value'] == 'foo'


def test_no_email(mapp, testapp):
    mapp.create_user("foo", password="foo", email=None)
    r = request_link(testapp, user_or_email='foo')
    (error,) = r.html.select('.error')
    assert error.text == 'Error: The specified user has no email address set.'
    (user_or_email,) = r.html.select('[name=user_or_email]')
    assert user_or_email.attrs['value'] == 'foo'


def test_deleted_user(dummy_mailer, mapp, testapp):
    mapp.create_user("foo", password="foo", email="foo@example.com")
    r = request_link(testapp, user_or_email='foo')
    (msg,) = dummy_mailer.outbox
    html = bs4.BeautifulSoup(msg.html, "html5lib")
    (link,) = html.select('a')
    mapp.login_root()
    mapp.delete_user("foo")
    r = testapp.xget(
        200, link.attrs['href'],
        headers=dict(accept="text/html"))
    (error,) = r.html.select('.error')
    assert error.text == "Error: The user 'foo' doesn't exist anymore."


def test_reuse(dummy_mailer, mapp, testapp):
    mapp.create_user("foo", password="foo", email="foo@example.com")
    r = request_link(testapp, user_or_email='foo')
    (msg,) = dummy_mailer.outbox
    html = bs4.BeautifulSoup(msg.html, "html5lib")
    (link,) = html.select('a')
    r = testapp.post(
        link.attrs['href'],
        code=200,
        params={
            'password': 'bar',
            'password2': 'bar',
            'submit': 'Set new password'},
        headers=dict(accept="text/html"))
    r = testapp.post(
        link.attrs['href'],
        code=200,
        params={
            'password': 'bar',
            'password2': 'bar',
            'submit': 'Set new password'},
        headers=dict(accept="text/html"))
    (error,) = r.html.select('.error')
    assert error.text == "Error: The password has already been changed since the link was requested."


def test_timeout(dummy_mailer, mapp, monkeypatch, testapp):
    import itsdangerous
    mapp.create_user("foo", password="foo", email="foo@example.com")
    r = request_link(testapp, user_or_email='foo')
    (msg,) = dummy_mailer.outbox
    html = bs4.BeautifulSoup(msg.html, "html5lib")
    (link,) = html.select('a')

    def loads(*args, **kw):
        raise itsdangerous.SignatureExpired("123")

    monkeypatch.setattr(itsdangerous.URLSafeTimedSerializer, "loads", loads)

    r = testapp.xget(
        200, link.attrs['href'],
        headers=dict(accept="text/html"))
    (error,) = r.html.select('.error')
    assert error.text == "Error: The password reset link has expired, request a new one."
