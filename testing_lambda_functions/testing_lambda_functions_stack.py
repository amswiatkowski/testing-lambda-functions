from aws_cdk import Stack
from aws_cdk import aws_apigateway
from aws_cdk import aws_iam
from aws_cdk import aws_lambda
from aws_cdk import aws_lambda_python_alpha
from aws_cdk import aws_ssm
from constructs import Construct


class TestingLambdaFunctionsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        lambda_layer = self._build_lambda_layer()
        lambda_role = self._build_lambda_role()
        self._build_ssm(lambda_role)
        my_lambda = self._build_lambda_function(lambda_role, lambda_layer)
        self._build_apigw(my_lambda)

    def _build_ssm(self, lambda_role):
        ssm = aws_ssm.StringParameter(scope=self, id='DummySSM', parameter_name='DummySSM',
                                      string_value='My Real SSM Value')

        ssm.grant_read(lambda_role)

    def _build_lambda_layer(self) -> aws_lambda_python_alpha.PythonLayerVersion:
        layer = aws_lambda_python_alpha.PythonLayerVersion(
            scope=self, id='LambdaLayer', entry='.build/common_layer',
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_9]
        )
        return layer

    def _build_lambda_role(self) -> aws_iam.Role:
        lambda_role = aws_iam.Role(scope=self, id='cdk-lambda-role',
                                   assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com'),
                                   role_name='cdk-lambda-role',
                                   managed_policies=[
                                       aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'service-role/AWSLambdaVPCAccessExecutionRole'),
                                       aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'service-role/AWSLambdaBasicExecutionRole')
                                   ])
        return lambda_role

    def _build_lambda_function(self,
                               lambda_role: aws_iam.Role,
                               lambda_layer: aws_lambda_python_alpha.PythonLayerVersion) -> aws_lambda_python_alpha.PythonFunction:
        my_lambda = aws_lambda_python_alpha.PythonFunction(
            scope=self, id='HelloHandler',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            entry='lambda_handlers',
            index='my_lambda.py',
            role=lambda_role,
            layers=[lambda_layer]
        )
        return my_lambda

    def _build_apigw(self, my_lambda: aws_lambda_python_alpha.PythonFunction) -> aws_apigateway:
        api = aws_apigateway.LambdaRestApi(scope=self, id="myapi", handler=my_lambda, proxy=False)
        root_resource = api.root.add_resource('store')
        store_resource = root_resource.add_resource('{user_id}')
        store_resource.add_method('GET')
