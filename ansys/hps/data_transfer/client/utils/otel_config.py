import os

def set_otel_config(exporter_url, resource_attributes=None,headers=None, exporter_type=None):
    """ Set data transfer worker Otel configuration using environment variables before starting data transfer worker
        ANSYS_DT_OTEL__EXPORTER_URL - Otel exporter url 
        ANSYS_DT_OTEL__RESOURCE_ATTRIBUTES - key-value pairs of resource attributes to be passed to the Otel SDK
        ANSYS_DT_OTEL__HEADERS - key-value pairs of headers to be associated with gRPC requests
        ANSYS_DT_OTEL__EXPORTER_TYPE - Otel exporter type
        ANSYS_DT_OTEL__ENABLED - enables Otel 
    """
    os.environ["ANSYS_DT_OTEL__ENABLED"] = "True"
    if exporter_type != None:
        os.environ["ANSYS_DT_OTEL__EXPORTER_URL"] = exporter_url
    if exporter_type != None:
        os.environ["ANSYS_DT_OTEL__EXPORTER_TYPE"] = exporter_type
    if resource_attributes != None:
        os.environ["ANSYS_DT_OTEL__RESOURCE_ATTRIBUTES"] = str(resource_attributes)
    if headers != None:
        os.environ["ANSYS_DT_OTEL__HEADERS"] = str(headers)
    
