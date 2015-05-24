"""A simple program to play Checkers with two people on the same computer.

I made it to play out checkers problems I found."""

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: End Users/Desktop
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Games/Entertainment
Topic :: Games/Entertainment :: Board Games
"""
name='checkers';version='0.2'
#---end of generally bits that generally need to be edited---

import sys
doc=__doc__.split("\n")

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

from distutils.core import setup
setup(\
    name=name,
    version=version,
    author="Jesse Weinstein",
    author_email="http://purl.org/NET/JesseW/email@purl.org",
    maintainer="Jesse Weinstein",
    maintainer_email="jessw@netwood.net",
    url="http://purl.oclc.org/NET/JesseW/Python",
    download_url="http://purl.oclc.org/NET/JesseW/SundryStuff/"\
    +name+"-"+version+".zip",
    license="http://www.opensource.org/licenses/mit-license.html",
    description=doc[0],
    long_description="\n".join(doc[2:]),
    classifiers = filter(None, classifiers.split("\n")),
    py_modules=[name]
    )
