from base64 import b64decode, b64encode
from devpi_server.auth import newsalt
from pyramid.view import view_config
from pyramid_mailer.message import Message
import hashlib
import itsdangerous
import py
import textwrap


def find_user(xom, user_or_email):
    user = xom.model.get_user(user_or_email)
    if user is None:
        for user in xom.model.get_userlist():
            if user.get().get('email') == user_or_email:
                break
        else:
            return None
    if user is None:
        return None
    return user


def to_bytes(data):
    if py.builtin._istext(data):
        return data.encode('ascii')
    return data


def generate_token(info, pwhash):
    token_hash = getattr(hashlib, info['hash_type'])()
    token_hash.update(to_bytes(info['salt']))
    token_hash.update(to_bytes(info['username']))
    token_hash.update(to_bytes(pwhash))
    return py.builtin._totext(b64encode(token_hash.digest()), encoding='ascii')


def get_pwhash(user):
    return user.get(credentials=True).get('pwhash', '')


def generate_link(request, user):
    xom = request.registry['xom']
    serializer = itsdangerous.URLSafeTimedSerializer(xom.config.secret)
    result = {
        'hash_type': 'sha256',
        'salt': newsalt(),
        'username': user.name}
    result['token'] = generate_token(result, get_pwhash(user))
    value = serializer.dumps(result)
    return request.route_url('passwd_reset', token=value)


def get_token_info(request, token):
    xom = request.registry['xom']
    serializer = itsdangerous.URLSafeTimedSerializer(xom.config.secret)
    value = serializer.loads(token, max_age=24 * 60 * 60)
    user = xom.model.get_user(value['username'])
    if user is None:
        raise ValueError("The user '%s' doesn't exist anymore." % value['username'])
    if value['token'] != generate_token(value, get_pwhash(user)):
        raise ValueError("The password has already been changed since the link was requested.")
    return value


def mail_link(request, email, link):
    html = textwrap.dedent("""\
        <p>Here is the requested password reset link:</p>
        <a href="{link}">{link}</a>
        <p>If you didn't request a password reset, just ignore this mail.</p>
        """.format(link=link))
    body = textwrap.dedent("""\
        Here is the requested password reset link:

        {link}

        If you didn't request a password reset, just ignore this mail.
        """.format(link=link))
    message = Message(
        subject="Devpi password reset",
        recipients=[email],
        body=body,
        html=html)
    request.registry['mailer'].send_immediately(message, fail_silently=False)


@view_config(
    route_name="passwd_reset_request",
    renderer="templates/passwd_reset_request.pt")
def password_reset_request_view(context, request):
    result = {
        'msg': None,
        'user_or_email': ''}
    if not request.POST:
        return result
    xom = request.registry['xom']
    user_or_email = request.POST['user_or_email']
    user = find_user(xom, user_or_email)
    if user is None:
        result['user_or_email'] = user_or_email
        result['error'] = 'No user with that name or email.'
        return result
    if not user.get().get('email'):
        result['user_or_email'] = user_or_email
        result['error'] = 'The specified user has no email address set.'
        return result
    link = generate_link(request, user)
    mail_link(request, user.get()['email'], link)
    result['msg'] = 'A mail with a link to reset your password has been sent.'
    return result


@view_config(
    route_name="passwd_reset",
    renderer="templates/passwd_reset.pt")
def password_reset_view(context, request):
    token = request.matchdict['token']
    result = {
        'msg': None,
        'token': token,
        'username': 'UNKNOWN'}
    try:
        info = get_token_info(request, token)
    except ValueError as e:
        result['error'] = py.builtin.text(e)
        return result
    except itsdangerous.SignatureExpired as e:
        result['error'] = "The password reset link has expired, request a new one."
        return result
    username = info['username']
    result['username'] = username
    if not request.POST:
        return result
    password = request.POST['password']
    password2 = request.POST['password2']
    if password != password2:
        result['error'] = "The entered passwords don't match."
        return result
    pm = request.registry['devpipasswdreset-pluginmanager']
    try:
        pm.hook.devpipasswdreset_validate(password=password)
    except ValueError as e:
        result['error'] = py.builtin.text(e)
        return result
    xom = request.registry['xom']
    user = xom.model.get_user(username)
    user.modify(password=password)
    result['msg'] = 'You successfully changed your password.'
    return result
