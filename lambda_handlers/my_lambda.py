import json
from typing import Dict
from aws_lambda_typing import context as context_, events
from aws_lambda_typing.events import APIGatewayProxyEventV1


def handler(event: events.APIGatewayProxyEventV1, context: context_):
    response = _prepare_response(json.loads(event.body))

    return response

def _prepare_response(event: APIGatewayProxyEventV1) -> Dict[str, any]:
    response = {
        "statusCode": 400,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": "Bad request"
    }
    print(event)

    return response