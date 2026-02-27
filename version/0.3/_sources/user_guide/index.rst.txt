.. _user_guide:

User guide
==========

This section explains how to interact with PyHPS Data Transfer.

To run the code samples in this section, you must have these prerequisites:

- A running Ansys HPS installation. For more information, see the
  `Ansys HPC Platform Services Deployment Guide <https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/prod_page.html?pn=Ansys%20HPC%20Platform%20Services&pid=HpcPlatformServices&lang=en>`_
  in the Ansys Help.
- A Python shell with PyHPS Data Transfer installed. For more information, see :ref:`getting_started`.

..
   This toctree must be a top-level index to display in
   pydata_sphinx_theme.

.. toctree::
   :maxdepth: 1
   :hidden:

   permissions
   run_async


Connect to a data transfer service client
-----------------------------------------

The data transfer service runs on the localhost with the default username and password. Before you can connect to
a data transfer service client, you must request the access token:

.. code-block:: python

    from ansys.hps.data_transfer.client.authenticate import authenticate

    hps_url = "https://localhost:8443/hps"
    auth_url = f"{hps_url}/auth/realms/rep"

    token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    token = token.get("access_token", None)

You can now use this access token to make a connection:

.. code-block:: python

    from ansys.hps.data_transfer.client import Client, DataTransferApi

    hps_url = "https://localhost:8443/hps"
    dt_url = f"{hps_url}/dt/api/v1"

    client = Client()
    client.binary_config.update(verbosity=3, debug=True, insecure=True, token=token, data_transfer_url=dt_url, log=True)
    client.start()

    api = DataTransferApi(client)
    api.status(wait=True)

Use this code to query available storages:

.. code-block:: python

    storages = api.storages()
    storage_names = [f"{storage['name']}({storage['type']})" for storage in storages]

Create a directory
------------------

Create a directory in a storage location:

.. code-block:: python

    base_dir = "basic-example"
            mkdir_op = api.mkdir([StoragePath(path=f"{base_dir}")])
        api.wait_for([mkdir_op.id])

Copy files
----------

When copying files, the ``local_path`` attribute is the path to the
files or directory to copy. The ``remote_path`` attribute is the path to
the remote directory to copy files to.

The paths used by the data transfer components follow this format:

``[remote or keyword]:/path/to/file.txt``

The ``[remote or keyword]`` part can be the name of a specific remote, ``any``, or be left empty. Specifying the name of a remote performs the given command only against it. Specifying ``any`` or leaving it empty runs the standard logic of the system and works through remotes in priority order.

If an operation should be performed against a local file or directory, remove the first part, including the colon.

**Examples:**

- ``any:mnt/test/path.txt``: A file in any of the available remotes.
- ``:mnt/test/path.txt``: Shorthand for any (``[]``).
- ``s3test:some/test/path.txt``: A file named ``s3test`` in a storage location.
- ``another/test/path.txt``: A local path.

Copy files between storage locations:

.. code-block:: python

    from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath

    src = [StoragePath(path=local_path, remote="local")]
    dst = [StoragePath(path=remote_path)]

    op = api.copy([SrcDst(src=src, dst=dst)])
    op = api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

List files
----------

List files in a specified directory:

.. code-block:: python

    op = api.list([StoragePath(path=base_dir)])
    op = api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")
    log.info(f"Files in {base_dir}: {op[0].result}")

Get metadata
------------

Get the metadata of a file in a specified directory:

.. code-block:: python

    op = api.get_metadata([StoragePath(path=f"{base_dir}/2.txt")])
    op = api.wait_for(op.id)
    md = op[0].result[f"{base_dir}/2.txt"]
    log.info(f"Metadata for {base_dir}/2.txt: {md}")

Remove files
------------

Remove files in a specified directory:

.. code-block:: python

    op = api.rmdir([StoragePath(path=base_dir)])
    op = api.wait_for([op.id])

Stop client
-----------

Stop the client:

.. code-block:: python

    client.stop()
