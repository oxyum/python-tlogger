from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
   long_description = f.read()

setup(
    name='tlogger',
    version='0.1.0',

    description='tlogger',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/oxyum/python-tlogger',

    # Author details
    author='Ivan Fedorov',
    author_email='oxyum@oxyum.ru',

    # Choose your license
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: System :: Logging',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.4',
    ],
    # What does your project relate to?
    keywords='logging',
    install_requires=[
       line.strip() for line in open('requirements.txt')
    ],
    zip_safe=False,
)
