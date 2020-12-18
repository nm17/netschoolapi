from setuptools import setup


with open("README.md") as readme:
    long_description = readme.read()


setup(
    name="netschoolapi",
    version="4.0.1",
    author="nm17",
    author_email="dannevergame@gmail.com",
    description="A fully asynchronous API wrapper for NetSchool written in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nm17/netschoolapi/",
    packages=["netschoolapi"],
    license="MIT",
    install_requires=["httpx", "dataclasses-json"],
    python_requires=">=3.7",
)
