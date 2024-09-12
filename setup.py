from setuptools import setup


def load_requirements(path):
    with open(path, "r") as file:
        return [line.strip() for line in file if line and not line.startswith("#")]


setup(
    name="algocomponents",
    version="1.0.1",
    packages=[
        "algocomponents",
        "algocomponents.tasks",
        "algocomponents.tasks.check_significance",
        "algocomponents.tasks.check_significance.sql",
        "algocomponents.tasks.downsample_table",
        "algocomponents.tasks.downsample_table.sql",
        "algocomponents.tasks.evaluate_prediction",
        "algocomponents.tasks.evaluate_prediction.sql",
        "algocomponents.tasks.model_trainers",
        "algocomponents.tasks.stratify_groups",
        "algocomponents.tasks.stratify_groups.sql",
        "algocomponents.tasks.stratify_groups.sqlite",
        "algocomponents.tasks.task_verifier",
        "algocomponents.tasks.task_verifier.sql",
        "algocomponents.utils",
        "algocomponents.adapters",
    ],
    install_requires=load_requirements("requirements.txt"),
    package_data={"": ["*.sql"]},
    url="",
    license="",
    author="erichorberg",
    author_email="eric.horberg@avaus.se",
    description="Tools for creating ML models in Python and SQL",
)
