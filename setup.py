from setuptools import setup


with open('README.md') as readme:
    long_description = readme.read()


setup(
    name='netschoolapi',
    version='7.1.8',
    description='Асинхронный API-клиент для «Сетевого города»',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='nm17',
    author_email='dannevergame@gmail.com',
    maintainer='igorlanov',
    maintainer_email='vonalrogi@ya.ru',
    url='https://github.com/nm17/netschoolapi/',
    packages=['netschoolapi'],
    package_data={'netschoolapi': ['py.typed']},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Topic :: Communications :: Chat',
        'Topic :: Education',
    ],
    license='MIT',
    install_requires=['httpx', 'marshmallow'],
    python_requires='>=3.8',
)
