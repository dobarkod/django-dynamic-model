#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'DjangoDynamicModel',
    version = '0.0.1',
    author = 'Marko Horvatic',
    author_email = 'marko.horvatic@goodcode.io',
    description = 'Django models that can save dynamic attributes to DB',
    license = 'MIT',
    url = 'http://goodcode.io/',
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    packages = find_packages(),

    include_package_data=True,

    install_requires = []
)
