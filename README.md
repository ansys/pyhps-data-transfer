# HPS Data Transfer Service Client
Python client library for HPS Data Transfer Service

### Prerequisites

Install pre-commit in your `global` python using

```
python -m pip install pre-commit
```
### Setup Environment

#### Linux:

```
python build.py dev
poetry shell
```
#### Windows:
```    
python3 build.py dev
poetry shell
```

### Build wheels
```    
python build.py wheel
```

### Test
```    
python build.py tests
```

### Generate Models
To generate the Data Transfer Service Client pydantic models, first download the Data Transfer Service Client OpenAPI specification and place it at the root folder, calling the file openapi2.json.
Then execute the `generate_models.sh` script. This will update the spec to openapi3, generate the models and attempt to format it. 
