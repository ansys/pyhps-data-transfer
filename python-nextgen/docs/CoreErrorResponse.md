# CoreErrorResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **str** |  | [optional] [default to 'something bad happened']

## Example

```python
from openapi_client.models.core_error_response import CoreErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CoreErrorResponse from a JSON string
core_error_response_instance = CoreErrorResponse.from_json(json)
# print the JSON string representation of the object
print CoreErrorResponse.to_json()

# convert the object into a dict
core_error_response_dict = core_error_response_instance.to_dict()
# create an instance of CoreErrorResponse from a dict
core_error_response_form_dict = core_error_response.from_dict(core_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


