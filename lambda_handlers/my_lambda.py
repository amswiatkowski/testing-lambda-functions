from typing import Any, Dict, Final

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_typing import events
from aws_lambda_typing.context import Context
from lambda_decorators import ssm_parameter_store
from mypy_boto3_lambda import LambdaClient

default_response: Final[Dict] = {
    "statusCode": 500,
    "headers": {
        "Content-Type": "application/json"
    },
    "body": "Internal Server Error"
}


# GET store/{user_id}
@ssm_parameter_store('RealSSM')
def handler(event: events.APIGatewayProxyEventV1, context: Context) -> Dict[str, Any]:
    logger: Logger = Logger()
    logger.info('Received event: ', extra={'event': event})
    try:
        response = _prepare_response(event['pathParameters'], context)
        logger.info('Sending response', extra={'response': response})
        return response
    except (KeyError, Exception) as exc:
        logger.info('Got fatal error', extra={'Exception': str(exc)})
        return default_response


def _prepare_response(request: Dict[str, Any], context: Context) -> Dict[str, Any]:
    ssm_parameter = context.parameters['RealSSM']
    if ssm_parameter is None:
        raise Exception
    response = {
        "statusCode": 400,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": "Bad request"
    }
    if request.get('user_id') is not None and len(request.get('user_id')) > 3:
        client: LambdaClient = boto3.client('lambda')
        boto3_response = client.list_layers()

        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": f"Hello Dummy! Here's what you're looking for: {ssm_parameter}. Pssst... here are my layers: {boto3_response['Layers']}"
        }

    return response
