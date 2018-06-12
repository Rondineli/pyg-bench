from setuptools import setup


setup(
    name='pyg-bench',
    version='0.1.1',
    description='Simple script to stress postgresql',
    long_description='This script is mainly to test database read/write',
    packages=[
        '.', 'templates'
        ],
    package_data={
        'templates': ['*']
    },
    url='https://github.com/Rondineli/pyg-bench',
    author='Rondineli Gomes de Araujo',
    author_email='rondineli.gomes.araujo@gmail.com',
    license='Apache',
    install_requires=[
        'psycopg2',
        'SQLAlchemy',
        'redis',
        'PrettyTable',
        'jinja2==2.10'
    ],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3',
    ],
    keywords='scripts postgres database',
    entry_points={
       "console_scripts": [
           "pyg-bench = orm:main",
       ]
    }
)
