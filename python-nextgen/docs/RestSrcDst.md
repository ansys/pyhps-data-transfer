# RestSrcDst


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dst** | [**RestStoragePath**](RestStoragePath.md) |  | 
**src** | [**RestStoragePath**](RestStoragePath.md) |  | 

## Example

```python
from openapi_client.models.rest_src_dst import RestSrcDst

# TODO update the JSON string below
json = "{}"
# create an instance of RestSrcDst from a JSON string
rest_src_dst_instance = RestSrcDst.from_json(json)
# print the JSON string representation of the object
print RestSrcDst.to_json()

# convert the object into a dict
rest_src_dst_dict = rest_src_dst_instance.to_dict()
# create an instance of RestSrcDst from a dict
rest_src_dst_form_dict = rest_src_dst.from_dict(rest_src_dst_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


