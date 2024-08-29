import tempfile

import pytest

from ansys.hps.data_transfer.client import DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState
from ansys.hps.data_transfer.client.models.permissions import Resource, RoleAssignment, RoleQuery, Subject


def test_permissions(storage_path, client, user_client, user_id):
    admin = DataTransferApi(client)
    admin.status(wait=True)
    user = DataTransferApi(user_client)
    user.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")

    remote_path = f"{storage_path}/my_file.txt"
    op = admin.copy([SrcDst(src=StoragePath(path=temp_file.name, remote="local"), dst=StoragePath(path=remote_path))])
    op = admin.wait_for([op], timeout=10)[0]
    assert op.state == OperationState.Succeeded

    with pytest.raises(Exception) as err_info:
        user.copy([SrcDst(src=StoragePath(path=remote_path), dst=StoragePath(path=f"{storage_path}/my_file_copy.txt"))])

    assert "403" in str(err_info.value)

    try:
        admin.set_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=storage_path, type="document"),
                    role="writer",
                    subject=Subject(id=user_id, type="user"),
                )
            ]
        )

        resp = admin.check_permissions(
            [
                RoleQuery(
                    resource=Resource(path=storage_path, type="document"),
                    role="reader",
                    subject=Subject(id=user_id, type="user"),
                )
            ]
        )

        assert resp.allowed

        resp = user.copy(
            [SrcDst(src=StoragePath(path=remote_path), dst=StoragePath(path=f"{storage_path}/my_file_copy.txt"))]
        )
        op = user.wait_for([resp.id], timeout=10)[0]
        assert op.state == OperationState.Succeeded
    finally:
        admin.remove_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=remote_path, type="document"),
                    role="writer",
                    subject=Subject(id=user_id, type="user"),
                )
            ]
        )
