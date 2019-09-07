import boto3
from os import environ
from botocore.exceptions import ClientError

client = boto3.client('dynamodb')

def handler(event, context):
    slug = str(event['pathParameters']['slug'])
    print(slug)
    # look for slug in ddb
    try:
        respose = client.get_item(
                TableName = environ['DDB_TABLE'],
                Key = {
                    'slug':{
                        'S' : slug
                    }
                }
        )

        if 'Item' in respose: # Item present
            # redirect the user
            original_link = respose['Item']['original_link']['S']
            return_value = {
                'statusCode':302, 
                'body':original_link,
                'headers':{
                    'Location': original_link,
                    'Content-Type': 'text/plain'
                }
            }

        else:
            # if 'Item' missing, report error
            return_value = {'statusCode': 400, 'body': 'Slug not found, please try again'}

    except:
        return_value = {'statusCode': 500, 'body': 'Error encountered, please try again later'}

    return return_value