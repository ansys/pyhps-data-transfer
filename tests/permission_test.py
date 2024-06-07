import tempfile
import time

from ansys.hps.dt_client.data_transfer import DataTransferApi
from ansys.hps.dt_client.data_transfer.models.ops import OperationState
from ansys.hps.dt_client.data_transfer.models.permissions import Resource, RoleAssignment, RoleQuery, Subject


def test_permissions(client, user_id):
    api_instance = DataTransferApi(client)
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")

    remote_path = "my_dir/my_file.txt"
    resp = api_instance.upload_file("any", remote_path, temp_file.name)
    operation_id = resp.id
    assert operation_id is not None
    for _ in range(10):
        time.sleep(0.5)
        op = api_instance.operations([operation_id])[0]
        if op.state in [OperationState.Succeeded, OperationState.Failed]:
            break
    # op = api_instance.wait_for([operation_id])[0]
    assert op.state == OperationState.Succeeded

    api_instance.set_permissions(
        [
            RoleAssignment(
                resource=Resource(path=remote_path, type="document"),
                role="writer",
                subject=Subject(id=user_id, type="user"),
            )
        ]
    )

    resp = api_instance.check_permissions(
        [
            RoleQuery(
                resource=Resource(path=remote_path, type="document"),
                role="reader",
                subject=Subject(id=user_id, type="user"),
            )
        ]
    )

    assert resp.allowed

    # resp = api_instance.copy([
    #     SrcDst(src=StoragePath(path=remote_path), dst=StoragePath(path="my_dir/my_file_copy.txt"))
    # ])
