import json
import boto3
import os
import uuid

table_name = os.environ.get("TABLE_NAME")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': '*',
}

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body)
    }

def handler(event, context):
    method = event['httpMethod']

    if method == 'POST':
        item = json.loads(event['body'])
        item['id'] = str(uuid.uuid4())
        table.put_item(Item=item)
        return build_response(200, {"id": item['id']})

    if method == 'GET':
        params = event.get('queryStringParameters') or {}
        empl_id = params.get('id')
        if not empl_id:
            return build_response(400, {'error': 'Missing required query parameter: id'})
        response = table.get_item(Key={'id': empl_id})
        if 'Item' in response:
            return build_response(200, response['Item'])
        else:
            return build_response(404, {'error': 'Employee not found'})

    return build_response(405, {'error': 'Method not allowed'})
