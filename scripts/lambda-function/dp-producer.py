import urllib.request
import boto3
import json
import os

def lambda_handler(event, context):
    API_KEY = os.getenv('API_KEY')
    STOCKS = ['TSLA', 'NVDA']
    FIREHOSE_STREAM = 'stock_data_data_stream'
    firehose = boto3.client('firehose')
    records = []

    for symbol in STOCKS:
        url = (f'https://alpha-vantage.p.rapidapi.com/query'
               f'?function=TIME_SERIES_INTRADAY&symbol={symbol}'
               f'&interval=1min&output_size=compact&datatype=json')
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': 'alpha-vantage.p.rapidapi.com'
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                for timestamp, values in data.get('Time Series (1min)', {}).items():
                    record = {
                        'symbol':    symbol,
                        'timestamp': timestamp,
                        'open':      float(values['1. open']),
                        'high':      float(values['2. high']),
                        'low':       float(values['3. low']),
                        'close':     float(values['4. close']),
                        'volume':    int(values['5. volume'])
                    }
                    records.append({'Data': json.dumps(record)})
        except Exception as e:
            print(f'Error processing {symbol}: {str(e)}')
            continue

    if records:
        firehose.put_record_batch(
            DeliveryStreamName=FIREHOSE_STREAM,
            Records=records
        )
    return {'statusCode': 200, 'body': f'Processed {len(records)} records'}
