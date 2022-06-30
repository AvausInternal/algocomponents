from setuptools import setup

setup(
    name='algocomponents',
    version='0.6.1',
    packages=[
        'algocomponents',
        'algocomponents.tasks',
        'algocomponents.tasks.model_evaluator',
        'algocomponents.tasks.model_evaluator.sql',
        'algocomponents.utils',
        'algocomponents.adapters',
    ],
    url='',
    license='',
    author='erichorberg',
    author_email='eric.horberg@avaus.se',
    description='Tools for creating ML models in Python and SQL'
)
