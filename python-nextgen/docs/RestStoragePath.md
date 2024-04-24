# RestStoragePath


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**path** | **str** |  | [default to 'my/path/to/data']
**remote** | **str** |  | [optional] [default to 'any']

## Example

```python
from openapi_client.models.rest_storage_path import RestStoragePath

# TODO update the JSON string below
json = "{}"
# create an instance of RestStoragePath from a JSON string
rest_storage_path_instance = RestStoragePath.from_json(json)
# print the JSON string representation of the object
print RestStoragePath.to_json()

# convert the object into a dict
rest_storage_path_dict = rest_storage_path_instance.to_dict()
# create an instance of RestStoragePath from a dict
rest_storage_path_form_dict = rest_storage_path.from_dict(rest_storage_path_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


