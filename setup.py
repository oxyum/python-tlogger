# -*- coding: utf-8; mode: python; -*-
import sys
from codecs import open  # To use a consistent encoding
from os import path

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='tlogger',
    version='0.1.1',
    description='Syntax sugar for logging.',
    long_description=long_description,
    author='Ivan Fedorov',
    author_email='oxyum@oxyum.ru',
    license='MIT',
    url='https://github.com/oxyum/python-tlogger',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: System :: Logging',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='logging',
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    install_requires=[],
    cmdclass={'test': PyTest},
    include_package_data=True,
    zip_safe=False,
)
