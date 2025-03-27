#!/usr/bin/env python
"""
Setup script for the Breaking Point MCP Agent
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from src/__init__.py
with open(os.path.join('src', '__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'").strip('"')
            break
    else:
        version = '0.1.0'

setup(
    name="bp-mcp-agent",
    version=version,
    description="Management Control Protocol (MCP) agent for Ixia Breaking Point",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ixia Breaking Point MCP Agent Team",
    author_email="info@example.com",
    url="https://github.com/example/BP_MCP_Agent",
    packages=find_packages(include=['src', 'src.*']),
    package_data={
        'src': ['py.typed'],
    },
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "matplotlib>=3.4.0",
        "pandas>=1.2.0",
        "PyYAML>=5.4.0",
        "python-dateutil>=2.8.1",
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.12.0',
            'black>=21.5b2',
            'isort>=5.9.1',
            'mypy>=0.812',
            'flake8>=3.9.2',
        ],
        'pdf': [
            'reportlab>=3.5.0',
        ],
        'async': [
            'aiohttp>=3.8.0',
            'asyncio>=3.4.3',
        ],
    },
    entry_points={
        'console_scripts': [
            'bp-agent=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Software Development :: Testing",
    ],
    keywords="network, testing, security, traffic-generation, api",
)
