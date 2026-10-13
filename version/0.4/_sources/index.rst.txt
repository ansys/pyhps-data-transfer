PyHPS Data Transfer documentation |version|
===========================================

Ansys HPC Platform Services (HPS) is a set of technology components designed to help you
manage the execution of simulations while making use of your full range of computing assets.
PyHPS Data Transfer is a Python client library for the HPS data transfer service. This
modular, plugin-based solution wraps around data transfer client REST APIs to help solve
complex data transfer problems for HPS.

With PyHPS Data Transfer, you can perform these operations:

* Create and list files.
* Copy files.
* Set and view permissions.
* Delete files.


.. grid:: 1 2 2 2


        .. grid-item-card:: Getting started :fa:`person-running`
            :padding: 2 2 2 2
            :link: getting_started/index
            :link-type: doc

            Learn how to install PyHPS Data Transfer in user mode and
            quickly start using it.

        .. grid-item-card:: User guide :fa:`book-open-reader`
            :padding: 2 2 2 2
            :link: user_guide/index
            :link-type: doc

            Understand the basics of how to interact with PyHPS Data Transfer.

        .. jinja:: main_toctree

            {% if build_api %}
            .. grid-item-card:: API reference :material-regular:`bookmark`
                :padding: 2 2 2 2
                :link: api/index
                :link-type: doc

                Understand how to use Python to interact programmatically with
                PyHPS Data Transfer.
            {% endif %}

            {% if build_examples %}
            .. grid-item-card:: Examples :fa:`scroll`
                :padding: 2 2 2 2
                :link: examples/index
                :link-type: doc

                Explore examples that show how to use PyHPS Data Transfer.
            {% endif %}

            .. grid-item-card:: Contribute :fa:`people-group`
                :padding: 2 2 2 2
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
