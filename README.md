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

### Openapi Version Conversion
To convert the Data Transfer Service Client Openapi version from 2.0 to 3.0 pull and run the following docker image:

```
docker pull swaggerapi/swagger-converter:v1.0.5
docker run -it -p 8080:8080 --name swagger-converter swaggerapi/swagger-converter:v1.0.5
```

The image contains a REST HTTP Endpoint (http://localhost:8080/index.html) that can be used to perform conversion.

### Generate Models
To generate the Data Transfer Service Client pydantic models, first download the Data Transfer Service Client OpenAPI specification, convert the Openapi version to 3.0 and save it as openapi.json in the root of the repository. Then, run the data model generator with this command:
```
datamodel-codegen --input .\openapi.json --input-file-type openapi --output ansys/rep/data/transfer/client/dtsc/models --output-model-type pydantic_v2.BaseModel
```