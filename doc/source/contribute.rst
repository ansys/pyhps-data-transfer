.. _contribute:

==========
Contribute
==========

Overall guidance on contributing to a PyAnsys library appears in
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyHPS Data Transfer.

The following contribution information is specific to PyHPS Data Transfer.


Install in developer mode
-------------------------

Installing PyHPS Data Transfer in developer mode allows you to modify and enhance the source:

#. Clone the repository:

   .. code:: bash

      git clone https://github.com/ansys/pyhps-data-transfer.git

#. Access the directory where you have cloned the repository:

   .. code:: bash

      cd pyhps-data-transfer

#. Create a clean Python virtual environment and activate it:

   .. code:: bash

      # Create a virtual environment
      python -m venv .venv

      # Activate it in a POSIX system
      source .venv/bin/activate

      # Activate it in a Windows CMD environment
      .venv\Scripts\activate.bat

      # Activate it in Windows Powershell
      .venv\Scripts\Activate.ps1

#. Install the package in editable mode with the required build system, documentation,
   and testing tools:

   .. code:: bash

      python -m pip install -U pip setuptools tox
      python -m pip install --editable .[tests,doc]

#. Verify your development installation:

   .. code:: bash

      tox

Test PyPyHPS Data Transfer
--------------------------

PyHPS Data Transfer takes advantage of `tox`_. This tool allows you to automate common development
tasks (similar to ``Makefile``), but it is oriented towards Python development.

Use ``tox``
^^^^^^^^^^^

While ``Makefile`` has rules, ``tox`` has environments. In fact, ``tox``
creates its own virtual environment so that anything being tested is isolated
from the project to guarantee the project's integrity.

The following environment commands are provided:

- ``tox -e style``: Checks for coding style quality.
- ``tox -e py``: Checks for unit tests.
- ``tox -e py-coverage``: Checks for unit testing and code coverage.
- ``tox -e doc``: Checks for documentation building.

Perform raw testing
^^^^^^^^^^^^^^^^^^^

If required, from the command line, you can call style commands like
`Ruff`_. You can also call unit testing commands like `pytest`_.
However, running these commands do not guarantee that your project is being tested
in an isolated environment, which is the reason why tools like ``tox`` exist.

Adhere to code style
--------------------

As indicated in `Coding style <https://dev.docs.pyansys.com/coding-style/index.html>`_
in the *PyAnsys developer's guide*, PyHPS Data Transfer follows PEP8 guidelines. PyHPS Data Transfer
implements `pre-commit`_ for style checking.

To ensure your code meets minimum code styling standards, run these commands::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  ruff.....................................................................Passed
  codespell................................................................Passed
  check for merge conflicts................................................Passed
  trim trailing whitespace.................................................Passed
  Validate GitHub Workflows................................................Passed
  Add License Headers......................................................Passed

Build documentation
-------------------

To build documentation manually, run these commands:

.. code:: bash

    python archive_examples.py
    make -C doc html

However, the recommended way of checking documentation integrity is to use
``tox``:

.. code:: bash

    tox -e doc && your_browser_name .tox/doc_out/index.html

Distribute
----------

If you would like to create either source or wheel files, start by installing
the building requirements and then executing the build module:

.. code:: bash

    python -m pip install -e .[build]
    python -m build
    python -m twine check dist/*


.. LINKS AND REFERENCES
.. _Ruff: https://docs.astral.sh/ruff/
.. _pytest: https://docs.pytest.org/en/stable/
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
