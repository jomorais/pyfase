from setuptools import setup, find_packages

setup(
    name='pyfase',
    version='1.0.5',
    url='https://github.com/jomorais/pyfase',
    license='GPLv3',
    author='Joaci Morais',
    author_email='joaci.morais@gmail.com',
    description='A Fast-Asynchronous-microService-Environment based on ZeroMQ.',
    packages=find_packages(),
    py_modules=['pyfase'],
    platforms='any',
    install_requires=['zmq'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Networking",
    ],
)
