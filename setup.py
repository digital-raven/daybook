import os
import subprocess as sp
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

# Find presets
convert_presets = []
for r, d, f in os.walk(path.join(here, 'presets', 'convert')):
    convert_presets = [path.join(r, f) for f in f]
    break

report_presets = []
for r, d, f in os.walk(path.join(here, 'presets', 'report')):
    report_presets = [path.join(r, f) for f in f]
    break

install_requires = []
if 'DEBBUILD' not in os.environ:
    install_requires = [
        'argcomplete >= 1.0',
        'prettytable',
        'pyaml',
        'superdate',
    ]

version=sp.check_output(['git','describe','--tags'], text=True).strip()

setup(
    name='daybook',
    version=version,
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
        ('etc/bash_completion.d', ['etc/daybook_completion.sh']),
        ('usr/share/man/man1', manfiles),
        ('usr/share/daybook/presets/convert', convert_presets),
        ('usr/share/daybook/presets/report', report_presets),
    ],
    entry_points={
        'console_scripts': [
            'daybook=daybook.client.main:main',
        ]
    },
)
