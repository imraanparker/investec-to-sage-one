import os
import sys

__title__ = "Import Investec to Sage One"
__version__ = "1.0.0"
__author__ = "Imraan Parker"
__authoremail__ = "imraan@techie.com"
__url__ = ""
__license__ = "MIT License"
__copyright__ = "Copyright 2020 Imraan Parker"

if sys.version_info < (3, 6):
    print("%s requires Python 3.6 or later." % __title__)
    sys.exit(1)

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

path = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(path, "README.md")).read()
except IOError:
    README = ""

with open("requirements.txt") as f:
    requirements = list()
    for r in f.read().splitlines():
        if not r.startswith("git+"):
            requirements.append(r)

setup(
    name=__title__,
    version=__version__,
    description="%s makes importing transactions from Investec to Sage One easy" % __title__,
    long_description=README,
    author=__author__,
    author_email=__authoremail__,
    url=__url__,
    packages=find_packages(exclude=["ez_setup"]),
    include_package_data=True,
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    zip_safe=False,
    license=__license__,
    classifiers=(
        "Development Status :: 3 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    )
)