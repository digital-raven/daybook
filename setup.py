import os
from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# Find man pages.
manfiles = []
for r, d, f in os.walk(path.join(here, 'docs', 'man')):
    manfiles = [path.join(r, f) for f in f if f.endswith('.1.gz')]
    break

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
    version='1.1.0-alpha',
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
        ('/usr/share/man/man1', manfiles),
    ],
    entry_points={
        'console_scripts': [
            'daybook=daybook.client.main:main',
            'daybookd=daybook.server.main:main',
        ]
    },
)
