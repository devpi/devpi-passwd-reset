from pluggy import HookspecMarker

hookspec = HookspecMarker("devpipasswdreset")


@hookspec
def devpipasswdreset_validate(password):
    """Called to validate a password.

    Raises ValueError which is used as message to the user.
    """
