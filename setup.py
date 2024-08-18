from setuptools import find_packages, setup

setup(
    name='enot_bot',
    version='0.2',
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