# Data Transfer Service Integration (https://github.com/ansys-internal/rep-data-transfer/issues/64)

# Description
The data transfer service is a replacement to the existing REP/HPS file transfer tool. This tool is utilized in the following technology components: PyHPS, Housekeeper, Evaluator, JMS, and JMS Web to handle storage and file operations. The data transfer service is comprised of two parts: a client and server. The server implementation is wrapped by a docker image and in the current internal release is exposed via the data-transfer profile. The client is available as a binary, docker image, and in a python wheel. Direct communication with the server implementation is typically conducted via the client. Integration of the new data transfer service into the existing stack should be done via the python data transfer client (https://github.com/ansys-internal/hps-data-transfer-client). This python client wraps the data transfer service client binary. In it's current iteration, the data transfer client binaries are included in the python data transfer service client wheel (https://github.com/ansys-internal/hps-data-transfer-client/releases). 

Note - there is one blocking item for each technology component integrating with the python data transfer service client. There does not appear to be an existing mechanism to install a python wheel via GitHub release. I've experimented with adding custom install steps (e.g. during build.py dev), but I have not had success with these steps properly functioning. During development, I've manually downloaded and installed the wheel locally in each virtual environment This issue needs resolve to fully build related docker technology components.

Alternative solutions:
1. Include client binaries inside the python data transfer service client repository :(
2. Expose new endpoint on the data transfer service to retrieve the client binary via REST

The following sections detail the current status of integration of the various technology components aforementioned.

## REP Deployments
As mentioned above, the current internal release contains a profile to start the applicable data-transfer releated services. (e.g. --profile data-transfer). There is an open PR to add permission and authorization configuration: https://github.com/ansys-internal/rep-deployments/pull/253.

Note - the pull request above requires changes from the rep shared configuration pull request (*see below).

## REP Shared Configuration
There is an open PR for adding permission configuration to the shared config: https://github.com/ansys-internal/rep-shared-config/pull/38. 

## PyHPS
There is an open PR to replace the old file transfer calls: https://github.com/ansys/pyhps/pull/422. This PR does not include the python data transfer service client and directly communicates with the data transfer service (server). The python data transfer service client is private and pyhps is public. This was the primary reason that I made the calls made direct, but I believe it should use the python client eventually.

I've conducted some preliminary testing by creating a project (and confirming files are created), but the changes need properly tested (including file download functionality).

Note - you will need to submit examples as repadmin due to permission related issues.

```
python project_setup.py -u repadmin -p repadmin
```

## Housekeeper
There is an open PR to replace the old file transfer calls in the file purging task and tests: https://github.com/ansys-internal/rep-housekeeper/pull/78.

I've conducted some preliminary testing by running the housekeeper outside of docker and confirming that the delete calls executed. The housekeeper should be properly built (docker image) and tested.

## Evaluator
There is an open PR to replace the old file transfer calls in the evaluator: https://github.com/ansys-internal/rep-evaluator/pull/556.

I've conducted some preliminary testing like the housekeeper, but evaluator needs properly tested alongside various technology components.

## JMS
There is an open PR to replace the old file transfer calls in JMS: https://github.com/ansys-internal/rep-job-management/pull/628. This item is on-going. I have replaced old file transfer calls in JMS outside tests. The tests need refactored and preliminary testing needs conducted. There were more changes here than originally expected.

## JMS Web
Created a new angular service DataTransferService that mimics methods defined within FileStorageService.
The idea is to have a drop-in replacement for the existing file transfer service calls. The development of this service was started, but all file manipulation pathways need examined and fully tested.

Here are the associated PRs for the current changes: https://github.com/ansys-internal/rep-job-management-web/pull/538 and https://github.com/ansys-internal/rep-common-web/pull/32