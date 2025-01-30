Permissions
-----------

The permissions plugin allows system admin to make sure that the 'root' directory has permissions set such that not every user can read/write to it.
System user names can be specified either in keycloak or using the user_mapping property
in order to get them from keycloak:
1. credentials need to be configured within the keycloak block for a user who has the ability to list other users and their attributes
2. every user who has a corresponding system username needs to have a custom attribute added in keycloak
3. the key must match the keycloak.attribute_name property
4. the value is the system username or it's numerical representation (ie. 1001)
user_mapping property:
1. needs to contain users' keycloak UUIDs as keys
2. values are the system usernames ** if a username comes from Active Directory, a numerical value should be used

Minimal example:

.. code-block:: JSON

    {
        "permissions":
            {
            "type": "acl-sync",
            "nested": {
                "type": "openfga", 
                "endpoint_url": "http://openfga:8080"
            },
            "root": "/shared/rep_file_storage",
            "user_mapping": {
                "a029a127-4371-43fc-a2bc-3c7f8621c183" : "my_user"
            },
            "keycloak":
                {
                "url": "http://keycloak:8080/hps/auth",
                "realm": "master",
                "username": "keycloak-admin",
                "password": "keycloak-admin-pwd",
                "user_realm": "rep",
                "attribute_name": "system_username"
                },
            },
    }


Connect to the Keycloak Admin API
----------------------------------

Connecting as a Keycloak administrator (using default credentials) gives you user id field:


.. code-block:: python

    from keycloak import KeycloakAdmin

    def get_user_id_from_keycloak():
        admin = KeycloakAdmin(
            server_url=keycloak_url + "/",
            username="keycloak",
            password="keycloak123",
            realm_name="rep",
            user_realm_name="master",
            verify=False,
        )
        user_id = admin.get_user_id("repuser")
        return user_id

RoleAssignment and RoleQuery
----------------------------

#TODO: Explain arguments to RoleAssignment and RoleQuery
Example usage of calls set_permissions() and check_permissions():

.. code-block:: python

    from ansys.hps.data_transfer.client.models.permissions import (
        Resource,
        ResourceType,
        RoleAssignment,
        RoleQuery,
        RoleType,
        Subject,
        SubjectType,
    )
    
    admin_client = Client()
    admin = DataTransferApi(admin_client)
    admin.status(wait=True)

    user_id = get_user_id_from_keycloak()

    try:
        admin.set_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role=RoleType.Writer,
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )
    except Exception as ex:
        log.info(ex)

    try:        
        resp = admin.check_permissions(
            [
                RoleQuery(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role=RoleType.Writer,
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )
    except Exception as ex:
        log.info(ex)


   
