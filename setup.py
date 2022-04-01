from setuptools import find_packages, setup

setup(
    name="orchestrator-demo",
    version="0.0.1",
    author="Company automation",
    author_email="automation@company.com",
    description="(Development tools for) workflow orchestrator",
    url="https://github.com/workfloworchestrator/orchestrator-demo",
    packages=find_packages(include=["company", "company.*"]),
    classifiers=["Programming Language :: Python :: 3", "Operating System :: OS Independent"],
    install_requires=[
        "more_itertools",
        "pydantic",
        # For now we assume these packages have been installed so we leave the lines below commented
        # uncomment the lines if you want the packages installed automatically as a dependency
        # "nwa-stdlib @ git+ssh://git@git.ia.surfsara.nl/automation/projects/nwa-stdlib.git@1.0.10#egg=nwa-stdlib",
    ],
    python_requires=">=3.9",
)
