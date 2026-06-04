from setuptools import setup

setup(
    name='recall-terminal',
    version='0.1.2',
    description='The AI brain for developers — natural language terminal commands',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    py_modules=['main'],
    install_requires=[
        'click',
        'anthropic',
        'rich',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'recall=main:recall',
        ],
    },
)