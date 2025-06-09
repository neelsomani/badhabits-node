from setuptools import setup, find_namespace_packages
import os

# Find packages in the badhabits directory
packages = find_namespace_packages(include=["badhabits*"])

setup(
    name="badhabits",
    version="0.1.0",
    description="Bad Habits Tracking Node",
    author="Neel Somani",
    author_email="neeljaysomani@gmail.com",
    packages=packages,
    install_requires=[
        "nodetools @ git+https://github.com/postfiatorg/nodetools.git",
        'sqlalchemy',
        'cryptography',
        'xrpl-py',
        'requests',
        'toml',
        'nest_asyncio',
        'psycopg2-binary',
        'openai',
        'loguru',
    ],
    python_requires=">=3.12",
    entry_points={
        'console_scripts': [
            'badhabits=badhabits.cli:main',
        ],
    },
) 