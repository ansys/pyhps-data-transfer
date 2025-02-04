Authentication service
======================

`Keycloak <https://www.keycloak.org>`_ is used for identity and access management. This open source
solution provides a variety of options for authentication and authorization. Users authenticate
with Keycloak rather than with the application, allowing flexibility in how the sign-in experience
is delivered.

The Keycloak API is exposed at ``https://hostname:port/hps/auth/api``, which is what the ``from ansys.hps.data_transfer.client.authenticate``
module wraps around.


Auth API
--------

.. module:: ansys.hps.data_transfer.client.authenticate

.. autosummary::
   :toctree: _autosummary

   authenticate