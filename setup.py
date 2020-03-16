from setuptools import setup


setup(
    name='netschoolapi',
    version='v1.4.5 0x1',
    description='Асинхронный API для NetSchool',
    url='https://github.com/igorlanov/netschoolapi/',

    packages=['netschoolapi'],
    install_requires=['aiohttp'],

    author='Ivan Gorlanov',

    license='MIT',
    licence_file='LICENSE',
)
