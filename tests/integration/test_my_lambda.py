from logging import Logger

import requests

from tests.helpers.cfn_reader import cfn_reader

logger: Logger = Logger(name='test_my_lambda')


def test_valid_get_ssm_parameter():
    url = cfn_reader()['MYAPIURL']
    logger.info(f'calling API URL: {url}')
    response = requests.get(url + 'store/1234')
    logger.info('got the response', extra={'response': response.content})
    assert response.status_code == 200


def test_invalid_get_ssm_parameter():
    url = cfn_reader()['MYAPIURL']
    logger.info(f'calling API URL: {url}')
    response = requests.get(url + 'store/1')
    logger.info('got the response', extra={'response': response.content})
    assert response.status_code == 400
