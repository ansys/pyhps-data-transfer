Run operations asynchronously
=============================

Run data transfer client operations asynchronously to improve performance and responsiveness.

Connect to a data transfer service
----------------------------------

Use the access token to connect to the data transfer service client:

.. code-block:: python

    from ansys.hps.data_transfer.client import Client, DataTransferApi

    hps_url = "https://localhost:8443/hps"
    dt_url = f"{hps_url}/dt/api/v1"

    client = AsyncClient(clean=True)

    client.binary_config.update(
        verbosity=3,
        debug=False,
        insecure=True,
        token=token,
        data_transfer_url=dt_url,
    )
    await client.start()

    api = AsyncDataTransferApi(client)
    await api.status(wait=True)

Query available storages:

.. code-block:: python

    storages = await api.storages()

Create a directory
------------------

Create a directory in the storage location:

.. code-block:: python

    base_dir = "basic-example"
    mkdir_op = await api.mkdir([StoragePath(path=f"{base_dir}")])
    await api.wait_for([mkdir_op.id])

Copy files
----------

Copy files between storage locations:

.. code-block:: python

    from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath

    src = [StoragePath(path=local_path, remote="local")]
    dst = [StoragePath(path=remote_path)]

    op = await api.copy([SrcDst(src=src, dst=dst)])
    op = await api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

List files
----------

List files in a specified directory:

.. code-block:: python

    op = await api.list([StoragePath(path=base_dir)])
    op = await api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")
    log.info(f"Files in {base_dir}: {op[0].result}")

Get metadata
------------

Retrieve metadata for a file in a specified directory:

.. code-block:: python

    op = await api.get_metadata([StoragePath(path=f"{base_dir}/2.txt")])
    op = await api.wait_for(op.id)
    md = op[0].result[f"{base_dir}/2.txt"]
    log.info(f"Metadata for {base_dir}/2.txt: {md}")

Remove files
------------

Delete files in a specified directory:

.. code-block:: python

    op = await api.rmdir([StoragePath(path=base_dir)])
    op = await api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

Stop client
-----------

Stop the client:

.. code-block:: python

    await client.stop()
