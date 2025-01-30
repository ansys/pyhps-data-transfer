# HPS Data Transfer Service Client
Python client library for HPS Data Transfer Service

### Prerequisites

Install poetry globally

```
python -m pip install poetry
```
### Setup Environment

```    
poetry install --all-groups --all-extras
```

### Build wheels
```    
poetry build
```

### Test
```    
poetry run pytest .
```

### Generate Models
To generate the Data Transfer Service Client pydantic models, first download the Data Transfer Service Client OpenAPI specification and place it at the root folder, calling the file openapi2.json.
Then execute the `generate_models.sh` script. This will update the spec to openapi3, generate the models and attempt to format it. 
