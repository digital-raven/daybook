from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), 'r', encoding='utf-8') as f:
    install_requires = []
    for line in f.readlines():
        commentless_line = line.split('#', 1)[0].strip()
        if commentless_line:
            install_requires.append(commentless_line)

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
    install_requires=install_requires,

    entry_points={
        'console_scripts': [
            'daybook=daybook.client:main',
            'daybookd=daybook.server:main',
        ]
    },
)
