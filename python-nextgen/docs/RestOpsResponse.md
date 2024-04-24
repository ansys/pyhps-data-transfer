# RestOpsResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operations** | [**List[OpsOperation]**](OpsOperation.md) |  | [optional] 

## Example

```python
from openapi_client.models.rest_ops_response import RestOpsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RestOpsResponse from a JSON string
rest_ops_response_instance = RestOpsResponse.from_json(json)
# print the JSON string representation of the object
print RestOpsResponse.to_json()

# convert the object into a dict
rest_ops_response_dict = rest_ops_response_instance.to_dict()
# create an instance of RestOpsResponse from a dict
rest_ops_response_form_dict = rest_ops_response.from_dict(rest_ops_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


