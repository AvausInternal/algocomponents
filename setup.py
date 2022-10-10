from setuptools import setup

setup(
    name="algocomponents",
    version="0.8.0",
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
    install_requires=[
        "google-cloud-bigquery==3.3.2",
        "pandas==1.4.3",
        "protobuf==4.21.6",
        "pyspark==3.3.0",
        "pytest==7.1.2",
        "setuptools==63.2.0",
        "db-dtypes",
        "scipy==1.9.1",
        "plotly==5.10.0",
        "kaleido==0.1.0post1",
    ],
    package_data={"": ["*.sql"]},
    url="",
    license="",
    author="erichorberg",
    author_email="eric.horberg@avaus.se",
    description="Tools for creating ML models in Python and SQL",
)
