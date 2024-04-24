# openapi_client.TokensApi

All URIs are relative to *http://localhost:8443/hps/dts/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**remotes_remote_tokens_post**](TokensApi.md#remotes_remote_tokens_post) | **POST** /remotes/{remote}/tokens | Create Tokens


# **remotes_remote_tokens_post**
> object remotes_remote_tokens_post(remote, paths)

Create Tokens

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
    api_instance = openapi_client.TokensApi(api_client)
    remote = 'remote_example' # str | Remote name
    paths = openapi_client.RestTokenRequest() # RestTokenRequest | Paths to create tokens for

    try:
        # Create Tokens
        api_response = api_instance.remotes_remote_tokens_post(remote, paths)
        print("The response of TokensApi->remotes_remote_tokens_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TokensApi->remotes_remote_tokens_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **remote** | **str**| Remote name | 
 **paths** | [**RestTokenRequest**](RestTokenRequest.md)| Paths to create tokens for | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Created |  -  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

