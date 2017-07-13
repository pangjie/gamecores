#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


setup(name='gamecores',
      packages=['gamecores'],
      version='0.1',
      description='A test for building Pypi package.',
      author='Jie Pang',
      author_email='riceknight@outlook.com',
      url='jpang.info',
      download_url='https://www.somewhere.com',
      include_package_date=True,
      install_requires=[
          # 'Click',
          # 'bs4',
          # 'requests',
          # 'tinydb',
      ],
      entry_points='''
        [console_scripts]
        gamecores=gamecores.gamecores:gc
      ''',)
