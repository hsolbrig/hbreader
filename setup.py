#!/usr/bin/env python
from setuptools import setup

# This needs to be here in order for the github dependency graph to work
NAME = "hbreader"

setup(
    setup_requires=['pbr'],
    pbr=True,
)
