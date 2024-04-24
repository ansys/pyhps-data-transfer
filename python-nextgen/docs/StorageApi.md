# openapi_client.StorageApi

All URIs are relative to *http://localhost:8443/hps/dts/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**storage_get**](StorageApi.md#storage_get) | **GET** /storage | Get storage configuration
[**storagecopy_post**](StorageApi.md#storagecopy_post) | **POST** /storage:copy | Copy data
[**storageexists_post**](StorageApi.md#storageexists_post) | **POST** /storage:exists | Check existence of files and directories
[**storagelist_post**](StorageApi.md#storagelist_post) | **POST** /storage:list | List a directory
[**storagemkdir_post**](StorageApi.md#storagemkdir_post) | **POST** /storage:mkdir | Create a directory
[**storagemove_post**](StorageApi.md#storagemove_post) | **POST** /storage:move | Move files and directories
[**storageremove_post**](StorageApi.md#storageremove_post) | **POST** /storage:remove | Remove files
[**storagermdir_post**](StorageApi.md#storagermdir_post) | **POST** /storage:rmdir | Remove a directory


# **storage_get**
> RestStorageConfigResponse storage_get()

Get storage configuration

Get storage configuration

### Example

```python
from __future__ import print_function
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8443/hps/dts/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8443/hps/dts/api/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.StorageApi(api_client)

    try:
        # Get storage configuration
        api_response = api_instance.storage_get()
        print("The response of StorageApi->storage_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StorageApi->storage_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**RestStorageConfigResponse**](RestStorageConfigResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **storagecopy_post**
> RestOpIdResponse storagecopy_post(operations)

Copy data

Copies files and directories

### Example

```python
from __future__ import print_function
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8443/hps/dts/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8443/hps/dts/api/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.StorageApi(api_client)
    operations = openapi_client.RestSrcDstOperations() # RestSrcDstOperations | Path to copy

    try:
        # Copy data
        api_response = api_instance.storagecopy_post(operations)
        print("The response of StorageApi->storagecopy_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StorageApi->storagecopy_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operations** | [**RestSrcDstOperations**](RestSrcDstOperations.md)| Path to copy | 

### Return type

[**RestOpIdResponse**](RestOpIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  * Operation-Id - ID of the operation <br>  * Location - Location to poll for operation status <br>  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **storageexists_post**
> RestOpIdResponse storageexists_post(operations)

Check existence of files and directories

Check existence of files and directories

### Example

```python
from __future__ import print_function
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8443/hps/dts/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8443/hps/dts/api/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.StorageApi(api_client)
    operations = openapi_client.RestPathOperations() # RestPathOperations | Path to check

    try:
        # Check existence of files and directories
        api_response = api_instance.storageexists_post(operations)
        print("The response of StorageApi->storageexists_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StorageApi->storageexists_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operations** | [**RestPathOperations**](RestPathOperations.md)| Path to check | 

### Return type

[**RestOpIdResponse**](RestOpIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  * Operation-Id - ID of the operation <br>  * Location - Location to poll for operation status <br>  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **storagelist_post**
> RestOpIdResponse storagelist_post(operations)

List a directory

List contents of a directory

### Example

```python
from __future__ import print_function
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8443/hps/dts/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8443/hps/dts/api/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.StorageApi(api_client)
    operations = openapi_client.RestPathOperations() # RestPathOperations | Directories to list

    try:
        # List a directory
        api_response = api_instance.storagelist_post(operations)
        print("The response of StorageApi->storagelist_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StorageApi->storagelist_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operations** | [**RestPathOperations**](RestPathOperations.md)| Directories to list | 

### Return type

[**RestOpIdResponse**](RestOpIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  * Operation-Id - ID of the operation <br>  * Location - Location to poll for operation status <br>  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **storagemkdir_post**
> RestOpIdResponse storagemkdir_post(operations)

Create a directory

Creates a new directory

### Example

```python
from __future__ import print_function
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8443/hps/dts/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8443/hps/dts/api/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.StorageApi(api_client)
    operations = openapi_client.RestPathOperations() # RestPathOperations | Directory to create

    try:
        # Create a directory
        api_response = api_instance.storagemkdir_post(operations)
        print("The response of StorageApi->storagemkdir_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StorageApi->storagemkdir_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operations** | [**RestPathOperations**](RestPathOperations.md)| Directory to create | 

### Return type

[**RestOpIdResponse**](RestOpIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  * Operation-Id - ID of the operation <br>  * Location - Location to poll for operation status <br>  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **storagemove_post**
> RestOpIdResponse storagemove_post(operations)

Move files and directories

Move files and directories

### Example

```python
from __future__ import print_function
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8443/hps/dts/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8443/hps/dts/api/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.StorageApi(api_client)
    operations = openapi_client.RestSrcDstOperations() # RestSrcDstOperations | Path to copy

    try:
        # Move files and directories
        api_response = api_instance.storagemove_post(operations)
        print("The response of StorageApi->storagemove_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StorageApi->storagemove_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operations** | [**RestSrcDstOperations**](RestSrcDstOperations.md)| Path to copy | 

### Return type

[**RestOpIdResponse**](RestOpIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  * Operation-Id - ID of the operation <br>  * Location - Location to poll for operation status <br>  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **storageremove_post**
> RestOpIdResponse storageremove_post(operations)

Remove files

Remove files

### Example

```python
from __future__ import print_function
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8443/hps/dts/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8443/hps/dts/api/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.StorageApi(api_client)
    operations = openapi_client.RestPathOperations() # RestPathOperations | Path to copy

    try:
        # Remove files
        api_response = api_instance.storageremove_post(operations)
        print("The response of StorageApi->storageremove_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StorageApi->storageremove_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operations** | [**RestPathOperations**](RestPathOperations.md)| Path to copy | 

### Return type

[**RestOpIdResponse**](RestOpIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  * Operation-Id - ID of the operation <br>  * Location - Location to poll for operation status <br>  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **storagermdir_post**
> RestOpIdResponse storagermdir_post(operations)

Remove a directory

Removes a new directory

### Example

```python
from __future__ import print_function
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8443/hps/dts/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8443/hps/dts/api/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.StorageApi(api_client)
    operations = openapi_client.RestPathOperations() # RestPathOperations | Directory to remove

    try:
        # Remove a directory
        api_response = api_instance.storagermdir_post(operations)
        print("The response of StorageApi->storagermdir_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StorageApi->storagermdir_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operations** | [**RestPathOperations**](RestPathOperations.md)| Directory to remove | 

### Return type

[**RestOpIdResponse**](RestOpIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  * Operation-Id - ID of the operation <br>  * Location - Location to poll for operation status <br>  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

