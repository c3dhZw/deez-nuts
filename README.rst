========
Overview
========

A(nother) e621 API library.

* Free software: GNU Lesser General Public License v3 (LGPLv3)

Installation
============

::

    pip install yippi

You can also install the in-development version with::

    pip install git+ssh://git@git.rorre.xyz/rorre/yippi.git@master

Documentation
=============


https://yippi.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
