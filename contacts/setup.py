#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='demo-contacts',
    version='0.0.1',
    description='Demo contacts service',
    packages=find_packages("src"),
    package_dir={},
    install_requires=[
        "nameko==2.11.0",
        "nameko-sqlalchemy==1.4.0",
        "mysql-connector-python==2.0.4",
        "nameko-autocrud==0.1.2",
        "nameko-slack==0.0.5",
    ],
    extras_require={
        'dev': [],
    },
    zip_safe=True
)
