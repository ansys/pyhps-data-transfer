# REP Data Transfer Service Client
Python client library for REP Data Transfer Service

### Prerequisites

Install pre-commit in your `global` python using

```
python -m pip install pre-commit
```
### Setup Environment

#### Linux:

```
python3 -m venv dev_env
source dev_env/bin/activate
python build.py dev
```
#### Windows:
```    
python3 -m venv dev_env
dev_env/Scripts/activate
python build.py dev
```

### Build
```    
python build.py dist
```

### Test
```    
python build.py tests
```

### Generate Models
To generate the Data Transfer Service Client pydantic models, first download the DTS Client OpenAPI specification and save it as openapi.json in the root of the repository. Then, run the data model generator with this command:
```
datamodel-codegen --input .\openapi.json --input-file-type openapi --output ansys/rep/data/transfer/client/dtsc/models --output-model-type pydantic_v2.BaseModel
```