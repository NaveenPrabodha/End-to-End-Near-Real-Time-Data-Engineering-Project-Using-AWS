import base64
import json
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    output = []
    for record in event['records']:
        try:
            decoded_data = base64.b64decode(record['data']).decode('utf-8')
            payload = json.loads(decoded_data)
            dt = datetime.strptime(payload['timestamp'], "%Y-%m-%d %H:%M:%S")
            transformed = {
                'symbol':   payload['symbol'],
                'datetime': payload['timestamp'],
                'open':     payload['open'],
                'high':     payload['high'],
                'low':      payload['low'],
                'close':    payload['close'],
                'volume':   payload['volume'],
                'date':     dt.date().isoformat(),
                'hour':     dt.hour
            }
            encoded_data = base64.b64encode(
                json.dumps(transformed).encode('utf-8')
            ).decode('utf-8')
            output.append({
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': encoded_data,
                'metadata': {
                    'partitionKeys': {
                        'symbol': payload['symbol'],
                        'date':   dt.date().isoformat(),
                        'hour':   str(dt.hour)
                    }
                }
            })
        except Exception as e:
            logger.error(f'Error: {str(e)}', exc_info=True)
            output.append({
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': record['data']
            })
    return {'records': output}
