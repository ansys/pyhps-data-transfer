.. _user_guide:

User guide
==========

This section walks you through the basics of how to interact with the Data transfer client service.

To reproduce the code samples provided in this section, you must have these
prerequisites:

- A running Ansys HPS installation. For more information, see the
  `Ansys HPC Platform Services Guide <https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/prod_page.html?pn=Ansys%20HPC%20Platform%20Services&pid=HpcPlatformServices&lang=en>`_
  in the Ansys Help.
- A Python shell with PyHPS Data Transfer installed. For more information, see :ref:`getting_started`.

..
   This toctreemust be a top level index to get it to show up in
   pydata_sphinx_theme

.. toctree::
   :maxdepth: 1
   :hidden:

   permissions
   run_async


Connect to a data transfer service
----------------------------------

You start by connecting to the data transfer service running on the localhost with the default username and password by first requesting access token:

.. code-block:: python

    from ansys.hps.data_transfer.client.authenticate import authenticate

    hps_url = "https://localhost:8443/hps"
    auth_url = f"{hps_url}/auth/realms/rep"

    token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    token = token.get("access_token", None)


Using the token, connect to the data transfer service client:

.. code-block:: python

    from ansys.hps.data_transfer.client import Client, DataTransferApi

    hps_url = "https://localhost:8443/hps"
    dt_url = f"{hps_url}/dt/api/v1"

    client = Client()
    client.binary_config.update(verbosity=3, debug=True, insecure=True, token=token, data_transfer_url=dt_url, log=True)
    client.start()

    api = DataTransferApi(client)
    api.status(wait=True)

Once connected, you can query storages available:

.. code-block:: python

    storages = api.storages()
    storage_names = [f"{storage['name']}({storage['type']})" for storage in storages]

Create a directory
------------------

To create a directory:

.. code-block:: python

    base_dir = "basic-example"
    mkdir_op = api.mkdir([StoragePath(path=f"{base_dir}")])
    api.wait_for([mkdir_op.id])

Copying files
----------------

In the following code block, local_path is path to the files or directory to transfer.
remote_path is path to the remote directory to transfer files to.
The paths used by the data transfer components look like

[remote or keyword]:/path/to/file.txt
The [remote or keyword] part can be either the name of a specific remote, "any", or empty. Empty and "any" amount to the same - running the standard logic of the system, working through remotes in priority order. Specifying the name of a remote performs the given command only against it.

If an operation should be performed against a local file or directory, the first part, including the colon, should be removed.

Examples:
any:mnt/test/path.txt - a file in any of the available remotes
:mnt/test/path.txt - shorthand for any:[]
s3test:some/test/path.txt - a file in storage called "s3test"
another/test/path.txt - a local path

To copy files:

.. code-block:: python

    from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath

    src = [StoragePath(path=local_path, remote="local")]
    dst = [StoragePath(path=remote_path)]

    op = api.copy([SrcDst(src=src, dst=dst)])
    op = api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

Listing files
----------------

To list files in a set path (base_dir in the following code block):

.. code-block:: python

    op = api.list([StoragePath(path=base_dir)])
    op = api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")
    log.info(f"Files in {base_dir}: {op[0].result}")


Getting metadata
----------------

To get metadata of files:

.. code-block:: python

    op = api.get_metadata([StoragePath(path=f"{base_dir}/2.txt")])
    op = api.wait_for(op.id)
    md = op[0].result[f"{base_dir}/2.txt"]
    log.info(f"Metadata for {base_dir}/2.txt: {md}")

Removing files
----------------

To get remove files:

.. code-block:: python

    op = api.rmdir([StoragePath(path=base_dir)])
    op = api.wait_for([op.id])

Stop client
----------------

To stop client:

.. code-block:: python

    client.stop()


