"""Knox-fortified JSON Web Tokens for Django REST Framework

"""

from setuptools import setup, find_packages
from codecs import open
from os import path

try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to reStructuredText")
    def read_md(f):
        with open(f, 'r', encoding='utf-8') as fh:
            text = fh.read()
        return text

here = path.abspath(path.dirname(__file__))


setup(
    name='drf-jwt-knox',
    version='0.1.0.dev1',
    description='JSON Web Tokens with a Knox-powered database backend',
    long_description=read_md('README.md'),
    url='https://github.com/ssaavedra/drf-jwt-knox',
    author='Santiago Saavedra',
    author_email='ssaavedra@gpul.org',
    license='Apache2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Session',
    ],
    # keywords='',
    packages=['jwt_knox'],
    install_requires=['djangorestframework~=3.4', 'django-rest-knox~=2.2', 'PyJWT~=1.4', 'six~=1.10'],
    extras_require={
        'dev': ['pypandoc~=1.2'],
        'test': ['coverage~=4.2', 'pytest~=3.0.2', 'tox~=2.3'],
    },
)
