import boto3
import string
from random import choice
from os import environ
from botocore.exceptions import ClientError
from urllib.parse import unquote

client = boto3.client('dynamodb')

part_to_skip = "link="
length_to_skip = len(part_to_skip)
choose_from = string.ascii_letters + string.digits

def response_for_failed(code = 0, error = "Error, please try again"):
    return {'statusCode': code, 'body': error}

def output_page(random_string, prefix, link):
    if prefix.endswith('/'):
        prefix = prefix[:-1]

    new_link = f"{prefix}/{random_string}"

    return_body = f'''
        <html>
            <body>
                <h3>URL {link} was shortened to:
                    <a href="{new_link}">{new_link}</a>
                </h3>
            </body>
        </html>
    '''

    return return_body


def format_link(link):
    link = link[length_to_skip:] # the format for variable 'link' will be link=www.xyz.com, skipping link= part
    link = unquote(link) # url decode link

    if not link.startswith("http://"):
        link = "http://" + link
    
    return link


def handler(event, context):
    if 'headers' in event and 'Referer' in event['headers']:
        prefix_of_shortened_url = event['headers']['Referer'] 
    else:
        # if request sent from curl or postman always deploy to dev stage only
        prefix_of_shortened_url = 'https://b9630u40yc.execute-api.us-east-1.amazonaws.com/dev'

    if 'body' in event: # 'body' in request
        # get new link user has requested to shorten
        link = event['body']
        link = format_link(link)

        # setting random slug for link, retry if slug already exists
        while True:
            random_string = ''.join(choice(choose_from) for _ in range(6))
            
            try:
                response = client.put_item(
                    TableName = environ['DDB_TABLE'],
                    Item = {'slug' : {'S' : random_string},
                            'original_link' : {'S' : link}
                    },
                    ConditionExpression = 'attribute_not_exists(original_link)'
                )

                break

            except ClientError as e:
                print("Duplicate Exists, Retrying...")
                continue
        
        # if successful response from dynamo db, show new URL to user
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return_value = {'statusCode': 200, 
            'body': output_page(random_string, prefix_of_shortened_url, link),
            'headers' : {'Content-Type': 'text/html'}
            }

        # if failure response from dynamo db, show error to user
        else:
            print("Problem Inserting", response)
            return_value = response_for_failed(code = 500)

    else: # 'body' not in request
        return_value = response_for_failed(code = 400)

    return return_value