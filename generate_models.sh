#!/bin/bash


docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
    -i /local/openapi2.json \
    -g openapi \
    -o /local/out --skip-validate-spec

dev_env/bin/datamodel-codegen --input ./out/openapi.json --input-file-type openapi --output ansys/hps/data_transfer/client/models --output-model-type pydantic_v2.BaseModel