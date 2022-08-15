#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from setuptools import setup

with open("svj_jobs_toolkit/include/VERSION", "r") as f:
    version = f.read().strip()

setup(
    name          = 'svj_jobs_toolkit',
    version       = version,
    license       = 'BSD 3-Clause License',
    description   = 'Description text',
    url           = 'https://github.com/tklijnsma/svj_jobs_toolkit.git',
    author        = 'Thomas Klijnsma',
    author_email  = 'tklijnsm@gmail.com',
    packages      = ['svj_jobs_toolkit'],
    package_data  = {'svj_jobs_toolkit': ['include/*']},
    include_package_data = True,
    zip_safe      = False,
    scripts       = []
    )
