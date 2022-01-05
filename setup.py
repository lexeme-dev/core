from setuptools import setup


setup(
    name='scl',
    version='0.1.0',
    py_modules=['cli'],
    install_requires=['Click'],
    entry_points={
        'console_scripts': [
            'scl = cli:cli'
        ]
    }
)
