# RestOpIdResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] [default to '2diK2kCkpgeHAQSNthIZ1JYyPte']
**location** | **str** |  | [optional] [default to '/api/v1/operations/2diK2kCkpgeHAQSNthIZ1JYyPte']

## Example

```python
from openapi_client.models.rest_op_id_response import RestOpIdResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RestOpIdResponse from a JSON string
rest_op_id_response_instance = RestOpIdResponse.from_json(json)
# print the JSON string representation of the object
print RestOpIdResponse.to_json()

# convert the object into a dict
rest_op_id_response_dict = rest_op_id_response_instance.to_dict()
# create an instance of RestOpIdResponse from a dict
rest_op_id_response_form_dict = rest_op_id_response.from_dict(rest_op_id_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


