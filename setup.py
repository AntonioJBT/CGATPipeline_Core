import glob
import sys
import os
import subprocess
import re

# Import setuptools
# Use existing setuptools, otherwise try ez_setup.
try:
    import setuptools
except ImportError:
    # try to get via ez_setup
    # ez_setup did not work on all machines tested as
    # it uses curl with https protocol, which is not
    # enabled in ScientificLinux
    import ez_setup
    ez_setup.use_setuptools()

from setuptools import setup, find_packages, Extension

from distutils.version import LooseVersion
if LooseVersion(setuptools.__version__) < LooseVersion('1.1'):
    print(("Version detected:", LooseVersion(setuptools.__version__)))
    raise ImportError(
        "the CGAT code collection requires setuptools 1.1 higher")

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
        'console_scripts': ['cgatpipe = CGATPipelines.cgatpipe:main']
    },
    # dependencies
    install_requires=install_requires,
    # other options
    zip_safe=False,
#    test_suite="tests",
)
