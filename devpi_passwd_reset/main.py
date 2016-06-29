from devpi_passwd_reset import hookspecs
from devpi_server.log import threadlog
from pluggy import PluginManager
import os
import sys
import yaml


def get_pluginmanager(load_entry_points=True):
    pm = PluginManager("devpipasswdreset", implprefix="devpipasswdreset_")
    pm.add_hookspecs(hookspecs)
    if load_entry_points:
        pm.load_setuptools_entrypoints("devpi_passwd_reset")
    pm.check_pending()
    return pm


def fatal(msg):
    threadlog.error(msg)
    sys.exit(1)


def devpiserver_pyramid_configure(config, pyramid_config):
    from pyramid_mailer import mailer_factory_from_settings
    # by using include, the package name doesn't need to be set explicitly
    # for registrations of static views etc
    pyramid_config.include('devpi_passwd_reset.main')
    settings = {}
    passwd_reset_config = config.args.passwd_reset_config
    if passwd_reset_config:
        if not os.path.exists(passwd_reset_config):
            fatal("No config at '%s'." % passwd_reset_config)
        with open(passwd_reset_config) as f:
            _config = yaml.load(f)
        settings.update(_config.get('pyramid_mailer', {}))
    pyramid_config.registry['mailer'] = mailer_factory_from_settings(settings)


def devpiserver_add_parser_options(parser):
    group = parser.addgroup("Password reset")
    group.addoption(
        "--passwd-reset-config", action='store',
        help="Password reset configuration file")


def devpipasswdreset_validate(password):
    if not password.strip():
        raise ValueError("The password can't be empty.")


def includeme(config):
    config.add_route(
        "passwd_reset_request",
        "/+password-reset")
    config.add_route(
        "passwd_reset",
        "/+password-reset/{token}")
    config.registry['devpipasswdreset-pluginmanager'] = get_pluginmanager()
    config.scan()
