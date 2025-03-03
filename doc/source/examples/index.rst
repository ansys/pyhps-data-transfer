.. _examples:

Examples
========

The examples in this section show how to use Pyhps data_transfer/client to
interact with data transfer service in Python.
Each example consists of a Python script plus a data file. 
You can execute many Python scripts with these command-line arguments:

* ``--local-path``: Path to the files or directory to transfer. Supports wildcards [default: None] [required]
* ``--remote-path``: Optional path to the remote directory to transfer files to [default: None]
* ``--url``: HPS URL to connect to [default: https://localhost:8443/hps] 
* ``--username``: HPS username (default: repadmin)
* ``--password``: HPS password (default: repadmin)
* ``--debug``: Enable debug logging [default: no-debug] 


.. toctree::
  :hidden:
  :maxdepth: 3

  ex_transfer_files
  ex_startup
  ex_permissions
  ex_run_async  

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - :ref:`example_transfer_files`
     - Basic script to transfer files to remote backends and back using data transfer service.
   * - :ref:`example_startup`
     - Script to startup Pyhps data_transfer/client components to use data transfer service components
   * - :ref:`example_permissions`
     - Script to set and query permissions on files
   * - :ref:`example_run_async`
     - Script to run async operations using data transfer service. 
