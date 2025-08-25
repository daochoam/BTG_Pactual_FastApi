from app.utils.create_table import create_table

tables = ["Users","Categories","BankFunds","UserBankFunds","UserBankFundsAudit"]

def dynamo_db():
    for table_name in tables:
        create_table(
            table_name=table_name,
            key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
            attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
        )