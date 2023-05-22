"""OpenIVN Python package configuration."""
from setuptools import setup

setup(
    name='openivn',
    version='1.0.0',
    packages=['openivn'],
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        'Flask==1.1.1',
        'requests==2.31.0',
        'gunicorn==19.9.0',
        'bs4==0.0.1',
        'beautifulsoup4==4.8.1',
        'oauthlib==3.1.0',
        'Flask-Login==0.4.1',
        'pyOpenSSL==19.1.0',
        'redis==3.4.1',
        'rq==1.2.2',
        'bitarray==1.2.11',
        'scipy==1.4.1',
        'numpy==1.18.3'
    ],
)
