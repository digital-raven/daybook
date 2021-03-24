import os
from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), 'r', encoding='utf-8') as f:
    long_description = f.read()

install_requires = []
if 'DEBBUILD' not in os.environ:
    install_requires = [
        'argcomplete >= 1.0',
        'dateparser >= 0.7.2, < 1.0',
        'python-dateutil >= 2.8, < 3.0',
        'prettytable',
    ]

setup(
    name='daybook',
    version='0.1.0-alpha',
    description='A command line ledger.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    author='Bo Cimino',
    author_email='ciminobo@protonmail.com',
    packages=find_packages(exclude=['tests']),
    license='Closed',
    python_requires='>3, <4',
    install_requires=install_requires,
    data_files=[
        ('/etc/daybook', ['etc/default.ini']),
        ('/etc/bash_completion.d', ['etc/daybook_completion.sh']),
    ],
    entry_points={
        'console_scripts': [
            'daybook=daybook.client.main:main',
            'daybookd=daybook.server.main:main',
        ]
    },
)
