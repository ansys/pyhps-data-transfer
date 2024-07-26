import concurrent.futures
import logging
import multiprocessing as mp

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi

log = logging.getLogger(__name__)


def _check_storage(dt_api):
    log.info(dt_api.storages())


def test_mp_support(client):
    api = DataTransferApi(client)
    api.status(wait=True)

    p = mp.Process(target=_check_storage, args=(api,))
    p.start()
    p.join()

    pool = concurrent.futures.ProcessPoolExecutor()
    f = pool.submit(_check_storage, api)
    concurrent.futures.wait([f])


async def test_async_mp_support(async_client):
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    p = mp.Process(target=_check_storage, args=(api,))
    p.start()
    p.join()

    pool = concurrent.futures.ProcessPoolExecutor()
    f = pool.submit(_check_storage, api)
    concurrent.futures.wait([f])
