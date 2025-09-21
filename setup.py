#!/usr/bin/env python3
"""
Setup script for Axiom Distinction Protocol (ADP)
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="axiom-distinction-protocol",
    version="1.0.0",
    author="ADP Foundation",
    description="A foundational authentication system based on pure logical principles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adp-foundation/axiom-distinction-protocol",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: Public Domain",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[],  # No dependencies - pure logical implementation
    extras_require={
        "dev": ["pytest", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "adp-demo=adp.demo:main",
            "adp-test=adp.tests.test_adp:run_tests",
            "adp-analyze=adp.analysis:run_performance_analysis",
        ],
    },
    project_urls={
        "Documentation": "https://github.com/adp-foundation/axiom-distinction-protocol/wiki",
        "Source": "https://github.com/adp-foundation/axiom-distinction-protocol",
        "Tracker": "https://github.com/adp-foundation/axiom-distinction-protocol/issues",
    },
)