from setuptools import setup
import os

from gibson_sessions import __version__


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='django-gibson-sessions',
    version=__version__,
    description="Gibson session backend for Django",
    long_description=read("README.rst"),
    keywords='django, gibson, sessions,',
    author='Mikalai Yurkin',
    author_email='yurkin.mikalai@gmail.com',
    url='https://github.com/mikalaiyurkin/django-gibson-sessions',
    license='MIT',
    packages=['gibson_sessions'],
    zip_safe=False,
    install_requires=['pygibson>=0.2.0'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
)
