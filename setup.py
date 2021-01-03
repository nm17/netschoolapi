from setuptools import setup


with open("README.md") as readme:
    long_description = readme.read()


setup(
    name="netschoolapi",
    version="4.0.3",
    author="nm17",
    author_email="dannevergame@gmail.com",
    maintainer="igorlanov",
    maintainer_email="vonalrogi@ya.ru",
    description="Асинхронный клиент для «Сетевого города»",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nm17/netschoolapi/",
    packages=["netschoolapi"],
    license="MIT",
    install_requires=["httpx", "dataclasses-json"],
    python_requires=">=3.7",
)
