# RestTokenRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**other** | **object** | For custom use | [optional] 
**read** | **List[str]** |  | [optional] 
**write** | **List[str]** |  | [optional] 

## Example

```python
from openapi_client.models.rest_token_request import RestTokenRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RestTokenRequest from a JSON string
rest_token_request_instance = RestTokenRequest.from_json(json)
# print the JSON string representation of the object
print RestTokenRequest.to_json()

# convert the object into a dict
rest_token_request_dict = rest_token_request_instance.to_dict()
# create an instance of RestTokenRequest from a dict
rest_token_request_form_dict = rest_token_request.from_dict(rest_token_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


