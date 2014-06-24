from setuptools import setup

requirements = open('requirements.txt').readlines()

setup(
    name = 'giab',
    version = '0.0.1a',
    author = 'Eder Sosa',
    author_email = 'eder.sohe@gmail.com',
    description = 'Genie in a Bottle Framework',
    long_description = ('Genie in a Bottle Framework,'
                       ' it\'s a set of wrappers and plugins on top of Bottle'
    	               ' (Python Web Framework) and easy deploy with'
    	               ' gunicorn+gevent'),
    scripts = ['giab'],
    install_requires = requirements,
    license = 'MIT',
    url = 'https://github.com/edersohe/giab'
)
