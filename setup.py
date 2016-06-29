from setuptools import setup
import os


def get_version(path):
    fn = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        path, "__init__.py")
    with open(fn) as f:
        for line in f:
            if '__version__' in line:
                parts = line.split("=")
                return parts[1].split("'")[1]


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGELOG = open(os.path.join(here, 'CHANGELOG.rst')).read()


setup(
    name="devpi-passwd-reset",
    description="devpi-passwd-reset: password reset view for devpi-web",
    long_description=README + "\n\n" + CHANGELOG,
    url="https://github.com/devpi/devpi-passwd-reset",
    version=get_version("devpi_passwd_reset"),
    maintainer="Florian Schulze",
    maintainer_email="florian.schulze@gmx.net",
    license="MIT",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python"] + [
            "Programming Language :: Python :: %s" % x
            for x in "2 3 2.7 3.4 3.5".split()],
    entry_points={
        'devpi_server': [
            "devpi-passwd-reset = devpi_passwd_reset.main"],
        'devpi_passwd_reset': [
            "devpi-passwd-reset = devpi_passwd_reset.main"]},
    install_requires=[
        'PyYAML',
        'devpi-web',
        'pyramid_mailer'],
    include_package_data=True,
    zip_safe=False,
    packages=['devpi_passwd_reset'])
