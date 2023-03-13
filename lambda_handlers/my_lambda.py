import json
from typing import Dict, Any, Final
from aws_lambda_typing import events
from aws_lambda_typing.context import Context
from lambda_decorators import ssm_parameter_store

default_response: Final[Dict] = {
    "statusCode": 500,
    "headers": {
        "Content-Type": "application/json"
    },
    "body": "Internal Server Error"
}

# GET store/{user_id}
@ssm_parameter_store('DummySSM')
def handler(event: events.APIGatewayProxyEventV1, context: Context) -> Dict[str, Any]:
    try:
        response = _prepare_response(event['pathParameters'], context)
        return response
    except (KeyError, Exception):
        return default_response


def _prepare_response(request: Dict[str, Any], context: Context) -> Dict[str, Any]:
    response = {
        "statusCode": 400,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": "Bad request"
    }
    if request.get('user_id') is not None and len(request.get('user_id')) > 3:
        ssm_parameter = context.parameters['DummySSM']
        if ssm_parameter is None:
            raise Exception
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "Hello Dummy! Here's what you're looking for: "+ssm_parameter
        }

    return response
