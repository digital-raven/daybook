from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='daybook',
    version='0.1.0',
    description='A command line ledger.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    author='Bo Cimino',
    author_email='ciminobo@protonmail.com',
    packages=find_packages(exclude=['tests']),
    license='Closed',
    python_requires='>3, <4',
    install_requires=[
        'dateparser >= 0.7.2, < 1.0',
        'argcomplete >= 1.0',
    ],
    data_files=[
        ('/etc/daybook', ['etc/default.ini']),
        ('/etc/bash_completion.d', ['etc/daybook_completion.sh']),
    ],
    entry_points={
        'console_scripts': [
            'daybook=daybook.client:main',
            'daybookd=daybook.server:main',
        ]
    },
)
