Manage permissions
------------------

System administrators use the ``permissions`` plugin to manage permissions on the ``root`` directory so that not every user can read or write to it.

Specify system usernames either in Keycloak or by using the ``user_mapping`` property.

- To get system usernames from Keycloak:

  #. Configure credentials within the Keycloak block for a user who can list other users and their attributes.
  #. Add a custom attribute in Keycloak for every user with a corresponding system username.
  #. Ensure that the key matches the ``keycloak.attribute_name`` property.
  #. Set the value to the system username or its numerical representation.

- To use the ``user_mapping`` property:

  #. Include the users' Keycloak UUIDs as keys.
  #. Set the values to the system usernames. Use a numerical value if the username comes from Active Directory.

Here is a simple example:

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

Connect to the ``KeycloakAdmin`` API
-------------------------------------

Connect as a Keycloak administrator using the default credentials to get the ``user_id`` field:

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

Set and check permissions
-------------------------

Use the ``set_permissions()`` and ``check_permissions()`` methods to set and check permissions.

The ``set_permissions()`` method takes a list of ``RoleAssignment`` objects with ``resource``, ``role``, and ``subject`` fields:

* ``resource``: Specifiesthe resource type with the directory path and resource type.
* ``role``: Assigns a role to the resource. Options are ``reader``, ``writer``, and ``administrator``.
* ``subject``: Passes the ``Subject`` and ``SubjectType`` with the user ID and user/group/any respectively.

Here is an example of how to use the ``set_permissions()`` method:

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

Similar to the ``set_permissions()`` method, the ``check_permissions`` method takes a list of ``RoleQuery`` objects with ``resource``, ``role``, and ``subject`` fields.

This code shows how to use the ``check_permissions()`` method:

.. code-block:: python

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
