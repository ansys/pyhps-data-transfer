# RestBuildInfo


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**branch** | **str** |  | [optional] 
**mode** | **str** |  | [optional] 
**revision** | **str** |  | [optional] 
**short_revision** | **str** |  | [optional] 
**version** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.rest_build_info import RestBuildInfo

# TODO update the JSON string below
json = "{}"
# create an instance of RestBuildInfo from a JSON string
rest_build_info_instance = RestBuildInfo.from_json(json)
# print the JSON string representation of the object
print RestBuildInfo.to_json()

# convert the object into a dict
rest_build_info_dict = rest_build_info_instance.to_dict()
# create an instance of RestBuildInfo from a dict
rest_build_info_form_dict = rest_build_info.from_dict(rest_build_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


