"""
Setup script for File Archiver.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="file-archiver",
    version="1.0.0",
    author="File Archiver Team",
    author_email="g.sousa@zohomail.eu",
    description="A maintainable, OOP Python file archiver for smart file organization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gsousav/file-archiver",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyPDF2>=3.0.0",
    ],
    extras_require={
        "full": [
            "python-magic>=0.4.27",
            "Pillow>=10.0.0",
            "imagehash>=4.3.1",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "file-archiver=file_archiver.ui.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "file_archiver": [
            "services/templates/*.css",
        ],
    },
)
