import boto3

def lambda_handler(event, context):
    client = boto3.client('athena', region_name='eu-north-1')
    client.start_query_execution(
        QueryString='MSCK REPAIR TABLE stock_prices',
        QueryExecutionContext={'Database': 'stock_db'},
        ResultConfiguration={
            'OutputLocation': 's3://dp-transformed-stock-data/athena-results/'
        }
    )
    return {'statusCode': 200, 'body': 'Partitions refreshed!'}
