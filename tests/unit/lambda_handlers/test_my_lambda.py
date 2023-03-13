import importlib.util
import logging
from typing import Final

import lambda_decorators
import pytest
from aws_lambda_typing.context import Context

from lambda_handlers.my_lambda import _prepare_response
from tests.unit.mocks.mock_ssm_parameter_store_decorator import mock_ssm_parameter_store_decorator

LAMBDA_EVENT = {
    "body": None,
    "resource": "/store",
    "path": "/store",
    "httpMethod": "POST",
    "isBase64Encoded": False,
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": {'user_id': '123-123-123-123'},
    "stageVariables": None,
    "headers": {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "en-US,en;q=0.8",
        "Cache-Control": "max-age=0",
        "CloudFront-Forwarded-Proto": "https",
        "CloudFront-Is-Desktop-Viewer": "True",
        "CloudFront-Is-Mobile-Viewer": "false",
        "CloudFront-Is-SmartTV-Viewer": "false",
        "CloudFront-Is-Tablet-Viewer": "false",
        "CloudFront-Viewer-Country": "US",
        "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Custom User Agent String",
        "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
        "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
        "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https"
    },
    "multiValueHeaders": {
        "Accept": [
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        ],
        "Accept-Encoding": [
            "gzip, deflate, sdch"
        ],
        "Accept-Language": [
            "en-US,en;q=0.8"
        ],
        "Cache-Control": [
            "max-age=0"
        ],
        "CloudFront-Forwarded-Proto": [
            "https"
        ],
        "CloudFront-Is-Desktop-Viewer": [
            "True"
        ],
        "CloudFront-Is-Mobile-Viewer": [
            "false"
        ],
        "CloudFront-Is-SmartTV-Viewer": [
            "false"
        ],
        "CloudFront-Is-Tablet-Viewer": [
            "false"
        ],
        "CloudFront-Viewer-Country": [
            "US"
        ],
        "Host": [
            "0123456789.execute-api.us-east-1.amazonaws.com"
        ],
        "Upgrade-Insecure-Requests": [
            "1"
        ],
        "User-Agent": [
            "Custom User Agent String"
        ],
        "Via": [
            "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)"
        ],
        "X-Amz-Cf-Id": [
            "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA=="
        ],
        "X-Forwarded-For": [
            "127.0.0.1, 127.0.0.2"
        ],
        "X-Forwarded-Port": [
            "443"
        ],
        "X-Forwarded-Proto": [
            "https"
        ]
    },
    "requestContext": {
        "accountId": "123456789012",
        "resourceId": "123456",
        "stage": "prod",
        "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
        "requestTime": "09/Apr/2015:12:34:56 +0000",
        "requestTimeEpoch": 1428582896000,
        "identity": {
            "cognitoIdentityPoolId": None,
            "accountId": None,
            "cognitoIdentityId": None,
            "caller": None,
            "accessKey": None,
            "sourceIp": "127.0.0.1",
            "cognitoAuthenticationType": None,
            "cognitoAuthenticationProvider": None,
            "userArn": None,
            "userAgent": "Custom User Agent String",
            "user": None
        },
        "path": "/store",
        "resourcePath": "/store",
        "httpMethod": "GET",
        "apiId": "1234567890",
        "protocol": "HTTP/1.1"
    }
}
LAMBDA_CONTEXT: Final[Context] = Context()

# Testing _prepare_response() function
def test_valid_prepare_response():
    context = LAMBDA_CONTEXT
    context.parameters = {'DummySSM': 'My Fake SSM Value'}
    request = {'user_id': '123-123-123'}
    # Check _prepare_response() when there's a valid request
    response = _prepare_response(request, context)
    # Lambda should return 200 Status
    logging.getLogger().info('Response body: ' + response['body'])
    assert response['statusCode'] == 200


def test_invalid_prepare_response():
    context = LAMBDA_CONTEXT
    context.parameters = {'DummySSM': 'My Fake SSM Value'}
    request = {'user_id': '123'}
    # Check _prepare_response() when there's a valid request
    response = _prepare_response(request, context)
    # Lambda should return 200 Status
    logging.getLogger().info('Response body: ' + response['body'])
    assert response['statusCode'] == 400


def test_without_ssm_prepare_response():
    with pytest.raises(Exception):
        context = LAMBDA_CONTEXT
        context.parameters = {}
        request = {'user_id': '123'}
        # Check _prepare_response() when there's a valid request
        response = _prepare_response(request, context)
        # Lambda should raise an Exception

# Testing Lambda's handler

def get_redecorated_handler():
    pytest.MonkeyPatch().setattr(lambda_decorators, 'ssm_parameter_store', mock_ssm_parameter_store_decorator)
    handler_spec = importlib.util.spec_from_file_location('redecorated_handler', 'lambda_handlers/my_lambda.py')
    handler_module = importlib.util.module_from_spec(handler_spec)
    handler_spec.loader.exec_module(handler_module)
    return handler_module.handler


def test_valid_my_lambda_handler():
    redecorated_handler = get_redecorated_handler()
    # Check Lambda behaviour when there's a valid LAMBDA_EVENT
    response = redecorated_handler(LAMBDA_EVENT, LAMBDA_CONTEXT)
    # Lambda should return 200 Status
    logging.getLogger().info('Response body: ' + response['body'])
    assert response['statusCode'] == 200


def test_empty_my_lambda_handler():
    redecorated_handler = get_redecorated_handler()
    # Check Lambda behaviour when there's no LAMBDA_EVENT at all
    response = redecorated_handler({}, LAMBDA_CONTEXT)
    # Lambda should return 500 Status as it was not properly invoked
    logging.getLogger().info('Response body: ' + response['body'])
    assert response['statusCode'] == 500


def test_invalid_my_lambda_handler():
    redecorated_handler = get_redecorated_handler()
    # Check Lambda behaviour when there's LAMBDA_EVENT with not-proper user_id
    LAMBDA_EVENT['pathParameters'] = {'user_id': '123'}
    response = redecorated_handler(LAMBDA_EVENT, LAMBDA_CONTEXT)
    # Lambda should return 400 Status as request's content has not proper value
    logging.getLogger().info('Response body: ' + response['body'])
    assert response['statusCode'] == 400
