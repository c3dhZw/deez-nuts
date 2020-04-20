#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from os.path import dirname
from os.path import join

from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fh:
        return fh.read()


setup(
    name="yippi",
    version="0.1.1",
    license="GPL-3.0-only",
    description="An (a)sync e621 API wrapper for Python.",
    long_description="%s\n%s"
    % (
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.rst")
        ),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    long_description_content_type="text/x-rst",
    author="Rendy Arya Kemal",
    author_email="rendyarya22@gmail.com",
    url="https://github.com/rorre/yippi",
    packages=["yippi"],
    package_data={'': ['LICENSE']},
    package_dir={"yippi": "yippi"},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://yippi.readthedocs.io/",
        "Changelog": "https://yippi.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/rorre/yippi/issues",
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires=">=3.6.*",
    install_requires=[
        "requests>=2.23.0", "aiohttp>=3.6.2"
    ],
    tests_require=[
        "pytest>=5.4.1", "pytest-recording>=0.7.0", "pytest-asyncio>=0.10.0",
        "vcrpy>=4.0.2"
    ],
)
