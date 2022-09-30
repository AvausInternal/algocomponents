from setuptools import setup

setup(
    name="algocomponents",
    version="0.7.0",
    packages=[
        "algocomponents",
        "algocomponents.tasks",
        "algocomponents.tasks.model_evaluator",
        "algocomponents.tasks.model_evaluator.sql",
        "algocomponents.tasks.task_verifier",
        "algocomponents.tasks.task_verifier.sql",
        "algocomponents.utils",
        "algocomponents.adapters",
    ],
    package_data={"": ["*.sql"]},
    url="",
    license="",
    author="erichorberg",
    author_email="eric.horberg@avaus.se",
    description="Tools for creating ML models in Python and SQL",
)
