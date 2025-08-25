import botocore
from app.config import dynamodb_client

def create_table(table_name, key_schema, attribute_definitions, provisioned_throughput=None):
    """
    Crea una tabla en DynamoDB si no existe.
    Si ya existe, ignora el error.
    """
    params = {
        "TableName": table_name,
        "KeySchema": key_schema,
        "AttributeDefinitions": attribute_definitions,
        "BillingMode": "PAY_PER_REQUEST" if provisioned_throughput is None else "PROVISIONED",
    }

    if provisioned_throughput:
        params["ProvisionedThroughput"] = provisioned_throughput

    try:
        dynamodb_client.create_table(**params)
        print(f"🚀 Tabla '{table_name}' creada con éxito")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            # Esto significa que la tabla ya existe
            print(f"✅ Tabla '{table_name}' ya existe")
        else:
            raise
