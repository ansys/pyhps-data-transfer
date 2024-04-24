# openapi_client.DataTransferApi

All URIs are relative to *http://localhost:8443/hps/dts/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**data_remote_path_get**](DataTransferApi.md#data_remote_path_get) | **GET** /data/{remote}/{path} | Download a file
[**data_remote_path_post**](DataTransferApi.md#data_remote_path_post) | **POST** /data/{remote}/{path} | Upload a file


# **data_remote_path_get**
> str data_remote_path_get(remote, path)

Download a file

Download a file

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
    api_instance = openapi_client.DataTransferApi(api_client)
    remote = 'any' # str | Remote name (default to 'any')
    path = 'path_example' # str | Path

    try:
        # Download a file
        api_response = api_instance.data_remote_path_get(remote, path)
        print("The response of DataTransferApi->data_remote_path_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataTransferApi->data_remote_path_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **remote** | **str**| Remote name | [default to &#39;any&#39;]
 **path** | **str**| Path | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **data_remote_path_post**
> RestOpIdResponse data_remote_path_post(remote, path, file)

Upload a file

Upload a file

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
    api_instance = openapi_client.DataTransferApi(api_client)
    remote = 'any' # str | Remote name (default to 'any')
    path = 'path_example' # str | Path
    file = openapi_client.bytearray() # bytearray | File

    try:
        # Upload a file
        api_response = api_instance.data_remote_path_post(remote, path, file)
        print("The response of DataTransferApi->data_remote_path_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataTransferApi->data_remote_path_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **remote** | **str**| Remote name | [default to &#39;any&#39;]
 **path** | **str**| Path | 
 **file** | **bytearray**| File | 

### Return type

[**RestOpIdResponse**](RestOpIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  * Operation-Id - ID of the operation <br>  * Location - Location to poll for operation status <br>  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

