from aws_cdk import Stack
from aws_cdk import aws_apigateway
from aws_cdk import aws_lambda_python_alpha
from aws_cdk import aws_lambda
from constructs import Construct


class TestingLambdaFunctionsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        layer = self._build_lambda_layer()
        my_lambda = self._build_lambda_function(layer)
        self._build_apigw(my_lambda)

    def _build_lambda_layer(self) -> aws_lambda_python_alpha.PythonLayerVersion:
        layer = aws_lambda_python_alpha.PythonLayerVersion(
            self, 'LambdaLayer', entry='.build/common_layer', compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_9]
        )
        return layer
    def _build_lambda_function(self, layer:  aws_lambda_python_alpha.PythonLayerVersion) -> aws_lambda_python_alpha.PythonFunction:
        my_lambda = aws_lambda_python_alpha.PythonFunction(
            self, 'HelloHandler',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            entry='lambda_handlers.my_lambda.handler',
            layers=[layer]
        )
        return my_lambda
    def _build_apigw(self, my_lambda: aws_lambda_python_alpha.PythonFunction) -> aws_apigateway:
        aws_apigateway.LambdaRestApi(self, "myapi", handler=my_lambda)
