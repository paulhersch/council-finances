from setuptools import setup, find_namespace_packages as find_packages

required_packages = []
with open("./requirements.txt", "r") as handle:
    required_packages = [line.split("\n")[0] for line in handle.readlines()]

setup(
    name="finanztool",
    version="0.0.1",
    description="""
        Simples Tool zur Finanzverwaltung, Entwickelt für den
        FSR Mathe/Info.
    """,
    include_package_data=True,
    packages=find_packages(),
    # package_dir={"": "src"},
    python_requires=">=3.11, <4",
    install_requires=required_packages,
    entry_points={"console_scripts": ["finanztool=finanztool:main"]},
)
