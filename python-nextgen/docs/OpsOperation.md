# OpsOperation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**children** | **List[str]** |  | [optional] 
**description** | **str** |  | [optional] 
**error** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**messages** | **List[str]** |  | [optional] 
**progress** | **float** |  | [optional] 
**result** | **object** |  | [optional] 
**state** | [**OpsOperationState**](OpsOperationState.md) |  | [optional] 

## Example

```python
from openapi_client.models.ops_operation import OpsOperation

# TODO update the JSON string below
json = "{}"
# create an instance of OpsOperation from a JSON string
ops_operation_instance = OpsOperation.from_json(json)
# print the JSON string representation of the object
print OpsOperation.to_json()

# convert the object into a dict
ops_operation_dict = ops_operation_instance.to_dict()
# create an instance of OpsOperation from a dict
ops_operation_form_dict = ops_operation.from_dict(ops_operation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


