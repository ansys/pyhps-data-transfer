# openapi_client.StatusApi

All URIs are relative to *http://localhost:8443/hps/dts/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**root_get**](StatusApi.md#root_get) | **GET** / | Get status


# **root_get**
> RestStatus root_get()

Get status

Get status of the server

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
    api_instance = openapi_client.StatusApi(api_client)

    try:
        # Get status
        api_response = api_instance.root_get()
        print("The response of StatusApi->root_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusApi->root_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**RestStatus**](RestStatus.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

