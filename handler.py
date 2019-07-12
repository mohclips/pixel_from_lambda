import json
import uuid
from message_broker_client import BrokerClient

import httpagentparser

# TESTING:  https://serverless.com/framework/docs/providers/aws/cli-reference/invoke-local/



# as per Kaan Erturk comment, it's important to declare any object
# that should live across requests, like a db client, OUTSIDE the function. In our example,
# a client for a message broker is declared here and initialized just once.
broker_client = BrokerClient()


# https://{LAMBDA_URL}/{LAMBDA_ENV}/pixel?page=https%3A%2F%2Fgithub.com%2Fjacopotagliabue
def get_pixel(event, context):
    """
    Ingest data and return a 1x1 gif pixel
    """
    # print the full event in CloudWatch for debugging purposes
    #print('event: '+json.dumps(event))
    headers = event.get('headers',None)
    request_context = event.get('requestContext',None)
    id = request_context.get('identity')
    ua_raw = headers.get('User-Agent','')
    ua = httpagentparser.detect(ua_raw)
    event_wrapper = {
        'eventId': str(uuid.uuid4()),  # assign a unique event id to the event
        'params': event.get('queryStringParameters',''),
        'lang': headers.get('Accept-Language',''),
        'country': headers.get('CloudFront-Viewer-Country',''),
        'referer': headers.get('Referer',''),
        'user_agent_raw': ua_raw,
        'user_agent': ua,
        'x_forward': headers.get('X-Forwarded-For',''),
        'req_time_epoch': request_context.get('requestTimeEpoch',''),
        'req_time': request_context.get('requestTime',''),
        'req_id': request_context.get('requestId',''),
        'sourceIP': id.get('sourceIp',''),
    }
    print('event_wrapper'+str(event_wrapper))
    # do something with the payload, e.g. send data to a message broker
    response = drop_message_to_broker(event_wrapper)
    # print broker response in CloudWatch for debugging purposes
    ###print('response: '+str(response))
    # finally return the 1x1 gif to the client
    return return_pixel_through_gateway()


def drop_message_to_broker(event):
    """
    Stub for generic function processing the event
    """
    # drop event to a broker and return a response
    broker_client.drop_message(event)
    return "Message {} dropped!".format(json.dumps(event))


def return_pixel_through_gateway():
    """
    Abstract the details of the lambda GIF response
    """
    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'image/gif',
            # https://www.imperva.com/learn/performance/cache-control/
            'Cache-Control': 'private, max-age=600'
        },
        "body": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
        "isBase64Encoded": True
    }
