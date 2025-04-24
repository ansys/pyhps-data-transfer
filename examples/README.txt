Examples
========

The examples in this section show how to use PyHPS Data Transfer to
interact in Python with a data transfer service.
Each example consists of a Python script plus a data file.

You can use these command-line arguments to execute Python scripts:

* ``--local-path``: Path to the files or directory to transfer. This argument supports wildcards. The default is ``None``.
* ``--remote-path``: Optional path to the remote directory to transfer files to. The default is ``None``.
* ``--url``: HPS URL to connect to. The default is ``https://localhost:8443/hps``.
* ``--username``: HPS username. The default is ``repadmin``.
* ``--password``: HPS password. The default is ``repadmin``.
* ``--debug``: Enable debug logging. The default is ``no-debug``.
