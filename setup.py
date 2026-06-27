from setuptools import setup, find_packages

setup(
    name='recall-terminal',
    version='1.0.0',
    description='The AI brain for developers — natural language terminal commands',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    py_modules=['main', 'config', 'auth', 'memory'],
    install_requires=[
        'click',
        'rich',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'recall=main:recall',
        ],
    },
    python_requires='>=3.9',
)