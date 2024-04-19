from aws_cdk import core
from aws_cdk.aws_cognito import UserPool
from aws_cdk.aws_lambda import Function, Runtime, Code, LayerVersion
from aws_cdk.aws_apigateway import LambdaRestApi
from aws_cdk import aws_iam as iam
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode

class FastAPIWithCognitoStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Cognito User Pool
        user_pool = UserPool(self, "UserPool",
            self_sign_up_enabled=True,
            removal_policy=core.RemovalPolicy.DESTROY,
            auto_verify={"email": True}
        )
        
        dependencies_layer = LayerVersion(self, "DependenciesLayer",
            compatible_runtimes=[Runtime.PYTHON_3_9],
            code=Code.from_asset("dependencies.zip"),
        )
        
        text_table = Table(self, "TextTable",
            table_name="test_text_table",
            partition_key=Attribute(name="user_id", type=AttributeType.STRING),
            sort_key=Attribute(name="timestamp", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY
        )
        
        handler = Function(self, "FastAPIFunction",
            runtime=Runtime.PYTHON_3_9,
            handler="main.handler",
            code=Code.from_asset(
                "lambda"
            ),
            environment={
                "COGNITO_USER_POOL_ID": user_pool.user_pool_id
            },
            layers=[dependencies_layer]
        )
        
        handler.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=["dynamodb:PutItem"],
                resources=[text_table.table_arn]
            )
        )
        
        text_table.grant_read_write_data(handler)
        
        api = LambdaRestApi(self, "FastAPIEndpoint",
            handler=handler,
            deploy_options={
                "stage_name": "dev"
            }
        )
        
        core.CfnOutput(self, "APIGatewayEndpoint",
            value=api.url
        )