Examples
========

The examples in this section show how to use PyHPS Data Transfer to
interact with data transfer service in Python.
Each example consists of a Python script plus a data file.
You can execute many Python scripts with these command-line arguments:

* ``--local-path``: Path to the files or directory to transfer. Supports wildcards [default: None] [required]
* ``--remote-path``: Optional path to the remote directory to transfer files to [default: None]
* ``--url``: HPS URL to connect to [default: https://localhost:8443/hps]
* ``--username``: HPS username (default: repadmin)
* ``--password``: HPS password (default: repadmin)
* ``--debug``: Enable debug logging [default: no-debug]
