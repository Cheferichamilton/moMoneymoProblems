# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='budgetbuddy',
    version='0.1.0',
    description='A simple budgeting tool with pay schedule and recurring bills, powered by Streamlit.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Cheferichamilton',
    url='https://github.com/Cheferichamilton/moMoneymoProblems',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'pandas',
        'plotly'
    ],
    entry_points={
        'console_scripts': [
            'budgetbuddy=budgetbuddy.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
