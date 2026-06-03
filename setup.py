from setuptools import setup

setup(
    name='recall-ai',
    version='0.1.0',
    py_modules=['main'],
    install_requires=[
        'click',
        'anthropic',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'recall=main:recall',
        ],
    },
)