devpi-passwd-reset: password reset view for devpi-web
=====================================================

This plugin adds a new view allowing users to reset their passwords.


Installation
------------

``devpi-passwd-reset`` needs to be installed alongside ``devpi-web``.

You can install it with::

    pip install devpi-passwd-reset

There are no further installation steps needed as ``devpi-server`` will automatically discover the plugin through calling hooks using the setuptools entry points mechanism.


Usage
-----

In a default installation, the view would be accessible at ``http://localhost:3141/+password-reset``.

Users can enter a user name or email address.
If a matching user exists and has the email set, a mail is sent with a link to set a new password.
The link is valid for 24h as long as the password wasn't changed in the meantime.

Configuration
-------------

You have to configure mail server settings by providing ``--passwd-reset-config=path_to_config``.

Create a yaml file with a dictionary containing another dictionary under the ``pyramid_mailer`` key.

You must at least provide the ``mail.default_sender`` setting.
By default ``mail.host`` is ``localhost`` and ``mail.port`` is ``25``.

See http://pythonhosted.org/pyramid_mailer/#configuration on configuration options available.

Example config:

.. code-block:: yaml

    pyramid_mailer:
        mail.port: 8025
        mail.default_sender: mail@example.com


devpi-passwd-reset plugin hooks
-------------------------------

Plugins can add password validation to enforce policies using the ``devpi_passwd_reset`` entry point in ``setup.py``.

.. code-block:: python

    def devpipasswdreset_validate(password):
        """Called to validate a password.

          Raises ValueError which is used as message to the user.
        """
