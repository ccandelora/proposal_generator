from setuptools import setup, find_packages

setup(
    name="proposal_generator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "crewai>=0.1.0",
        "python-dotenv>=0.19.0",
        "openai>=1.3.0",
    ],
    entry_points={
        'console_scripts': [
            'generate-proposal=proposal_generator.cli:main',
        ],
    },
) 