from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="git-doc-gen",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Git commit history documentation generator with visual diffs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/git-doc-gen",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "GitPython>=3.1.40",
        "click>=8.1.7",
        "rich>=13.7.0",
        "Pillow>=10.1.0",
        "matplotlib>=3.7.3",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "git-doc-gen=src.cli:main",
        ],
    },
)