from setuptools import setup, find_packages

setup(
    name="shyfem_toolbox",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib"
    ],
    author="Your Name",
    description="A toolbox for handling custom files",
    url="https://github.com/alepaladio/shyfem_toolbox",
    python_requires=">=3.7",
)
