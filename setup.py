from setuptools import setup, find_packages

setup(
    name="dojocommons",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pydantic~=2.10.6",
        "duckdb~=1.2.1",
        "boto3~=1.37.18",
        "pydantic-settings~=2.8.1",
    ],
    description="Classes comuns para o projeto Dojo Management.",
    author="Rodrigo Gregori",
    license="MIT",
)
