PyHPS Data Transfer documentation |version|
===========================================

Ansys HPC Platform Services (HPS) is a set of technology components designed to help you
manage the execution of simulations while making use of your full range of computing assets.
Data transfer service is a modular, plugin-based solution, which helps to solve complex data transfer problems for HPS.
PyHPS Data Transfer brings HPS data transfer client to your Python app.
Wrapping around data transfer client REST APIs, PyHPS Data Transfer allows you to:

* Create and list files.
* Copy files.
* Set and view permissions.


.. grid:: 1 1 2 2
        :gutter: 2

        .. grid-item-card:: Getting started :fa:`person-running`
            :link: getting_started/index
            :link-type: doc

            Learn how to install and start using PyHPS Data Transfer.

        .. grid-item-card:: User guide :fa:`book-open-reader`
            :link: user_guide/index
            :link-type: doc

            Understand the basics of how to interact with PyHPS Data Transfer.

        .. grid-item-card:: API reference :material-regular:`bookmark`
            :padding: 2 2 2 2
            :link: api/index
            :link-type: doc

            Understand how to use Python to interact programmatically with
            PyHPS Data Transfer .

        .. jinja:: main_toctree

            {% if build_examples %}

                .. grid-item-card:: Examples :fa:`scroll`
                    :link: examples/index
                    :link-type: doc

                    Explore examples that show how to use PyHPS Data Transfer.
            {% endif %}

            .. grid-item-card:: Contribute :fa:`people-group`
                :link: contribute
                :link-type: doc

                Learn how to contribute to the PyHPS Data Transfer codebase
                or documentation.

.. jinja:: main_toctree

    .. toctree::
        :hidden:
        :maxdepth: 3

        getting_started/index
        user_guide/index
        {% if build_examples %}
        examples/index
        {% endif %}
        {% if build_api %}
        api/index.rst
        {% endif %}
        contribute
