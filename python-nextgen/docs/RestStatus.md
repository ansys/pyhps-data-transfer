# RestStatus


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**build_info** | [**RestBuildInfo**](RestBuildInfo.md) |  | [optional] 
**time** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.rest_status import RestStatus

# TODO update the JSON string below
json = "{}"
# create an instance of RestStatus from a JSON string
rest_status_instance = RestStatus.from_json(json)
# print the JSON string representation of the object
print RestStatus.to_json()

# convert the object into a dict
rest_status_dict = rest_status_instance.to_dict()
# create an instance of RestStatus from a dict
rest_status_form_dict = rest_status.from_dict(rest_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


