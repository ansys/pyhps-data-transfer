import os

from setuptools import find_namespace_packages, setup

root = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(root, "ansys", "hps", "data_transfer", "client", "__version__.py"), "r") as f:
    exec(f.read(), about)

install_requires = [
    "pydantic>=2.7.1",
    "httpx>=0.27.0,<0.29.0",
    "backoff>=2.2.1",
    "humanfriendly>=10.0",
    "requests>=2.21.0",
    "portend>=3.2.0",
    "filelock>=3.14.0",
    "psutil>=5.9.1",
    "asyncio-atexit>=1.0.0",
]


def setup_package():
    metadata = dict(
        name="ansys-hps-data-transfer-client",
        version=about["__version__"],
        packages=find_namespace_packages(include=["ansys.*"]),
        author="ANSYS, Inc.",
        description="HPS data transfer service client",
        long_description="See README.md",
        long_description_content_type="text/x-markdown",
        project_urls={},
        python_requires=">=3.10",
        install_requires=install_requires,
        package_data={"": ["bin/*"]},
        include_package_data=True,
        classifiers=[
            "License :: OSI Approved :: MIT License",
        ],
        extras_require={},
    )

    setup(**metadata)


if __name__ == "__main__":
    setup_package()
