import tempfile

import pytest

from ansys.hps.dt_client.data_transfer import DataTransferApi
from ansys.hps.dt_client.data_transfer.models.msg import SrcDst, StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState
from ansys.hps.dt_client.data_transfer.models.permissions import Resource, RoleAssignment, RoleQuery, Subject


def test_permissions(client, user_client, user_id):
    admin = DataTransferApi(client)
    user = DataTransferApi(user_client)
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")

    remote_path = "my_dir/my_file.txt"
    resp = admin.upload_file("any", remote_path, temp_file.name)
    operation_id = resp.id
    assert operation_id is not None
    op = admin.wait_for([operation_id], timeout=10)[0]
    assert op.state == OperationState.Succeeded

    with pytest.raises(Exception):
        user.copy([SrcDst(src=StoragePath(path=remote_path), dst=StoragePath(path="my_dir/my_file_copy.txt"))])

    try:
        admin.set_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=remote_path, type="document"),
                    role="writer",
                    subject=Subject(id=user_id, type="user"),
                )
            ]
        )

        resp = admin.check_permissions(
            [
                RoleQuery(
                    resource=Resource(path=remote_path, type="document"),
                    role="reader",
                    subject=Subject(id=user_id, type="user"),
                )
            ]
        )

        assert resp.allowed

        resp = user.copy([SrcDst(src=StoragePath(path=remote_path), dst=StoragePath(path="my_dir/my_file_copy.txt"))])
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
