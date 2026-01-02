from setuptools import find_packages, setup

setup(
    name="enot_bot",
    version="1.7.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["Flask[async]", "requests", "telebot", "telethon", "sqlalchemy"],
)
