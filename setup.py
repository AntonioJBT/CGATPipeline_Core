'''
setup for |project_name|

Python packaging can become a nightmare, check the following for reference:
For example on setting a Python package, see:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
https://python-packaging.readthedocs.io/en/latest/index.html
http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/index.html

For Python 3.5
Before packaging or installing run:

    pip install -U pip twine check-manifest setuptools

TO DO: to add tests see https://python-packaging.readthedocs.io/en/latest/testing.html

To package, do something like this:

    check-manifest
    python setup.py check
    python setup.py sdist bdist_wheels

which will create a dist/ directory and a compressed file inside with your package.

More notes and references in:
    https://github.com/EpiCompBio/welcome

And in the Python docs.
Upload to PyPI after this if for general use.
'''
#################
# Get modules

# Py3 to 2 from pasteurize:
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

#from builtins import open
#from builtins import str
#from future import standard_library
#standard_library.install_aliases()

# To use a consistent encoding
from codecs import open

# Standard modules:
import sys
import os
import glob

# Always prefer setuptools over distutils:
import setuptools

from setuptools import setup, find_packages

# To run custom install warning use:
from setuptools.command.install import install

from distutils.version import LooseVersion
if LooseVersion(setuptools.__version__) < LooseVersion('1.1'):
    print ("Version detected:", LooseVersion(setuptools.__version__))
    raise ImportError(
        "Setuptools 1.1 or higher is required")

# Get location to this file:
here = os.path.abspath(os.path.dirname(__file__))
print(here)


################################
# collect CGAT version
sys.path.insert(0, "scripts")
import version

version = version.__version__

################################
# Define dependencies 

major, minor1, minor2, s, tmp = sys.version_info

if (major == 2 and minor1 < 7) or major < 2:
    raise SystemExit("""CGAT requires Python 2.7 or later.""")


# Get Ptyhon modules required:
install_requires = []

with open(os.path.join(here, 'requirements.rst'), encoding='utf-8') as required:
    for line in (required):
        if not line.startswith('#') and not line.startswith('\n'):
            line = line.strip()
            install_requires.append(line)

print(install_requires)


cgat_packages = find_packages(exclude=["scripts*"])

# rename scripts to CGATScripts
cgat_packages.append("CGATScripts")

cgat_package_dirs = {'CGAT': 'CGAT',
                     'CGATScripts': 'scripts',
                     'CGATPipelines': 'CGATPipelines'}

##########################################################
##########################################################
# Classifiers
classifiers = """
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved
Programming Language :: Python
Topic :: Software Development
Topic :: Scientific/Engineering
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

setup(
    # package information
    name='CGATPipelines',
    version=version,
    description='CGAT : the Computational Genomics Analysis Toolkit',
    author='Andreas Heger',
    author_email='andreas.heger@gmail.com',
    license="MIT",
    platforms=["any"],
    keywords="computational genomics",
    long_description='CGAT : the Computational Genomics Analysis Toolkit',
    classifiers=[_f for _f in classifiers.split("\n") if _f],
    url="http://www.cgat.org/cgat/Tools/",
    # package contents
    packages=cgat_packages,
    package_dir=cgat_package_dirs,
    include_package_data=True,
    entry_points={
        'console_scripts': ['pipeline_quickstart = scripts.pipeline_quickstart:main']
    },
    # dependencies
    install_requires=install_requires,
    # other options
    zip_safe=False,
#    test_suite="tests",
)
