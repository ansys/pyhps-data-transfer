import os
import sys

from setuptools import find_namespace_packages, setup

root = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(root, "ansys", "rep", "data", "transfer", "client", "__version__.py"), "r") as f:
    exec(f.read(), about)

install_requires = ["pydantic==2.4.2", "httpx==0.26.0"]

priv_modules = {
    "ansys-rep-common[sql,falcon,crypto,redis,otel]": (
        " git+https://github.com/ansys-internal/rep-common-py.git@main#egg=ansys-rep-common"
    )
}

if "--no-priv" in sys.argv:
    sys.argv.remove("--no-priv")
else:
    install_requires.extend([f"{k} @ {v}" for k, v in priv_modules.items()])


def setup_package():
    metadata = dict(
        name="ansys-rep-data-transfer-client",
        version="0.1.0",
        packages=find_namespace_packages(include=["ansys.*"]),
        author="ANSYS, Inc.",
        description="REP data transfer service client",
        long_description="See README.md",
        long_description_content_type="text/x-markdown",
        project_urls={},
        python_requires=">=3.10",
        install_requires=install_requires,
        package_data={"ansys.rep.data.transfer.client": ["bin/*"]},
        include_package_data=True,
        extras_require={},
    )

    setup(**metadata)


if __name__ == "__main__":
    setup_package()
