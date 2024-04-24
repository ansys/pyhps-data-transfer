# openapi_client.OperationsApi

All URIs are relative to *http://localhost:8443/hps/dts/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**operations_get**](OperationsApi.md#operations_get) | **GET** /operations | Get operations
[**operationsbatch_post**](OperationsApi.md#operationsbatch_post) | **POST** /operations:batch | Get operations


# **operations_get**
> RestOpsResponse operations_get(ids)

Get operations

Get detailed information about an operation

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
    api_instance = openapi_client.OperationsApi(api_client)
    ids = ['ids_example'] # List[str] | Operation ids

    try:
        # Get operations
        api_response = api_instance.operations_get(ids)
        print("The response of OperationsApi->operations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->operations_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ids** | [**List[str]**](str.md)| Operation ids | 

### Return type

[**RestOpsResponse**](RestOpsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **operationsbatch_post**
> RestOpsResponse operationsbatch_post(ids)

Get operations

Get detailed information about an operation

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
    api_instance = openapi_client.OperationsApi(api_client)
    ids = openapi_client.RestOpsRequest() # RestOpsRequest | Operation ids

    try:
        # Get operations
        api_response = api_instance.operationsbatch_post(ids)
        print("The response of OperationsApi->operationsbatch_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->operationsbatch_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ids** | [**RestOpsRequest**](RestOpsRequest.md)| Operation ids | 

### Return type

[**RestOpsResponse**](RestOpsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

