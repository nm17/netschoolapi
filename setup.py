from setuptools import setup

setup(
    name="netschoolapi",
    version="1.4.0",
    packages=["netschoolapi"],
    url="https://github.com/nm17/netschoolapi/",
    license="MIT",
    author="nm17",
    author_email="dannevergame@gmail.com",
    description="A fully asynchronous API wrapper for NetSchool written in Python",
    long_description=open("README.md").read(),
    install_requires=["httpx", "trio", "python-dateutil", 'pandas'],
    python_requires=">=3.6",
    long_description_content_type='text/markdown',
)
