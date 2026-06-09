#!/usr/bin/env python3
"""
Setup script for CodeReview-AI-CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="codereview-ai-cli",
    version="1.0.0",
    author="gitstq",
    author_email="",
    description="🦞 Lightweight Terminal Code Review & Quality Analysis Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/CodeReview-AI-CLI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "codereview-ai=codereview_ai.cli:main",
        ],
    },
    keywords="code-review quality-analysis static-analysis cli terminal developer-tools git",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/CodeReview-AI-CLI/issues",
        "Source": "https://github.com/gitstq/CodeReview-AI-CLI",
    },
)
