from setuptools import setup


setup(
    name="socless_repo_parser",
    version="0.1.0",
    description="A example Python package",
    url="https://github.com/twilio-labs/socless_repo_parser",
    author="Saxon Hunt",
    author_email="saxon.h@outlook.com",
    packages=["socless_repo_parser"],
    install_requires=[
        "pydantic",
        "docstring-parser",
        "ruamel.yaml==0.17.4",
        "pygithub==1.55",
    ],
)
