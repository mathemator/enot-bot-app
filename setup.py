from setuptools import setup, find_packages

setup(
    name='enot_bot',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'Flask[async]',
        'requests',
        'telebot',
        'telethon',
        'sqlalchemy'
    ],
)