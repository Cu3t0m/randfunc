import sys
from codecs import open  # To use a consistent encoding
from os import path

# Always prefer setuptools over distutils
from setuptools import (setup, find_packages)

here = path.abspath(path.dirname(__file__))
install_requirements = find_packages()

pypi_operations = frozenset(['register', 'upload']) & frozenset([x.lower() for x in sys.argv])
if pypi_operations:
    raise ValueError('Command(s) {} disabled in this example.'.format(', '.join(pypi_operations)))


with open(path.join(here, 'README.md'), encoding='utf-8') as fh:
    long_description = fh.read()


__version__ = None
exec(open('randfunc/about.py').read())
if __version__ is None:
    raise IOError('about.py in project lacks __version__!')

setup(name='randfunc', version=__version__,
      author='Cu3t0m',
      description='A collection of random python functions.',
      long_description=long_description,
      license='BSD',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      include_package_data=True,
      install_requires=install_requirements,
      keywords=['module', 'functions', 'utility'],
      url="https://github.com/Cu3t0m/randfunc",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
      ])
