# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

NAME = 'pyprobs'
VERSION = '0.2'
DESCRIPTION = 'A module that returns True or False output based on given probability'
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
URL = 'https://github.com/OmerFI/PyProbs'
AUTHOR = 'Ömer Furkan İşleyen'
AUTHOR_EMAIL = 'omergumushane@hotmail.com'
LICENSE = 'MIT'
KEYWORDS = 'Probability, Chance'

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    keywords=KEYWORDS,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    py_modules=["PyProbs"]
)
