from aws_cdk import (CfnOutput, Duration, RemovalPolicy, Stack, aws_apigateway,
                     aws_iam, aws_lambda, aws_lambda_python_alpha, aws_ssm)
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
from testing_lambda_functions.constants import (API_HANDLER_LAMBDA_MEMORY_SIZE,
                                                API_HANDLER_LAMBDA_TIMEOUT,
                                                BUILD_FOLDER,
                                                LAMBDA_ARCHITECTURE,
                                                LAMBDA_RUNTIME,
                                                POWER_TOOLS_LOG_LEVEL,
                                                POWERTOOLS_SERVICE_NAME,
                                                SERVICE_NAME)


class TestingLambdaFunctionsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        api = self._build_apigw()
        lambda_layer = self._build_lambda_layer()
        lambda_role = self._build_lambda_role()
        self._build_ssm(lambda_role)
        my_lambda = self._build_lambda_function(lambda_role, lambda_layer)
        root_resource = api.root.add_resource('store')
        store_resource = root_resource.add_resource('{user_id}')
        store_resource.add_method('GET', integration=aws_apigateway.LambdaIntegration(handler=my_lambda))

    def _build_ssm(self, lambda_role):
        ssm = aws_ssm.StringParameter(scope=self, id='RealSSM', parameter_name='RealSSM',
                                      string_value='My Real SSM Value')

        ssm.grant_read(lambda_role)

    def _build_lambda_layer(self) -> aws_lambda_python_alpha.PythonLayerVersion:
        layer = aws_lambda_python_alpha.PythonLayerVersion(
            scope=self, id='LambdaLayer', entry='.build/common_layer', compatible_architectures=[LAMBDA_ARCHITECTURE],
            compatible_runtimes=[LAMBDA_RUNTIME], removal_policy=RemovalPolicy.DESTROY
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
                                   ],
                                   inline_policies={
                                       'lambdas_configurations': aws_iam.PolicyDocument(
                                           statements=[
                                               aws_iam.PolicyStatement(
                                                   actions=['lambda:ListLayers'],
                                                   resources=['*'],
                                                   effect=aws_iam.Effect.ALLOW,
                                               )
                                           ]
                                       )})
        return lambda_role

    def _build_lambda_function(self,
                               lambda_role: aws_iam.Role,
                               lambda_layer: aws_lambda_python_alpha.PythonLayerVersion) -> aws_lambda.Function:
        lambda_function = aws_lambda.Function(
            self,
            'HelloHandler',
            runtime=LAMBDA_RUNTIME,
            architecture=aws_lambda.Architecture.ARM_64,
            code=aws_lambda.Code.from_asset(BUILD_FOLDER),
            handler='lambda_handlers.my_lambda.handler',
            environment={
                POWERTOOLS_SERVICE_NAME: SERVICE_NAME,  # for logger, tracer and metrics
                POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger

            },
            tracing=aws_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[lambda_layer],
            role=lambda_role,
            log_retention=RetentionDays.ONE_DAY,
            log_format=aws_lambda.LogFormat.JSON.value,
            system_log_level=aws_lambda.SystemLogLevel.INFO.value,
        )
        aws_lambda.Alias(self, id='HelloHandlerAlias', alias_name='hello-handler', version=lambda_function.current_version)
        return lambda_function

    def _build_apigw(self) -> aws_apigateway.RestApi:
        rest_api: aws_apigateway.RestApi = aws_apigateway.RestApi(
            self,
            'service-rest-api',
            rest_api_name='Service Rest API',
            description='This service handles /api/store requests',
            deploy_options=aws_apigateway.StageOptions(throttling_rate_limit=2, throttling_burst_limit=10),
            cloud_watch_role=False,
        )

        CfnOutput(self, id='MY_API_URL', value=rest_api.url)

        return rest_api
