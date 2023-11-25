from logging import Logger
from typing import Dict

import boto3
from mypy_boto3_cloudformation import CloudFormationClient
from testing_lambda_functions.app import get_stack_name

logger: Logger = Logger(name='cfn_reader')


def cfn_reader() -> Dict[str, str]:
    cf_client: CloudFormationClient = boto3.client('cloudformation')
    response = cf_client.describe_stacks(StackName=get_stack_name())
    outputs = {}
    for output in response["Stacks"][0]["Outputs"]:
        outputs.update({output["OutputKey"]: output["OutputValue"]})
    logger.info(f'Got the following outputs: {outputs}', extra={'outputs': outputs})
    print(f'Got the following outputs: {outputs}')
    return outputs
