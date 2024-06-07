import os
import tempfile
import time

from ansys.hps.dt_client.data_transfer import DataTransferApi
from ansys.hps.dt_client.data_transfer.models.ops import OperationState
from ansys.hps.dt_client.data_transfer.models.permissions import Resource, RoleAssignment, Subject


def test_permissions(client, user_id):
    api_instance = DataTransferApi(client)
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    resp = api_instance.upload_file("any", os.path.basename(temp_file.name), temp_file.name)
    operation_id = resp.id
    assert operation_id is not None
    for _ in range(10):
        time.sleep(0.5)
        op = api_instance.operations([operation_id])[0]
        if op.state in [OperationState.Succeeded, OperationState.Failed]:
            break
    assert op.state == OperationState.Succeeded

    api_instance.set_permissions(
        [
            RoleAssignment(
                resource=Resource(path=os.path.basename(temp_file.name), type="document"),
                role="reader",
                subject=Subject(id=user_id, type="user"),
            )
        ]
    )

    # assert len(resp.permissions) == 0
