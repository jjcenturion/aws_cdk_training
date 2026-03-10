from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_apigateway,
    aws_lambda,
    aws_dynamodb
)
from constructs import Construct

class RestApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB BillingMode options:
        #
        # 1. BillingMode.on_demand()
        #    - PAY_PER_REQUEST: charges per individual read/write request.
        #    - No capacity planning required. Scales automatically.
        #    - Ideal for unpredictable traffic or new/dev projects.
        #
        # 2. BillingMode.provisioned(read_capacity, write_capacity)  [Table - old API]
        #    Billing.provisioned(read_capacity, write_capacity)       [TableV2 - new API]
        #    - Reserves fixed capacity units (RCU and WCU) billed per hour.
        #    - Cheaper when traffic is high and predictable.
        #    - Supports Auto Scaling to adjust capacity automatically.
        #    - Example:
        #      billing=aws_dynamodb.Billing.provisioned(
        #          read_capacity=aws_dynamodb.Capacity.fixed(5),
        #          write_capacity=aws_dynamodb.Capacity.autoscaled(min_capacity=1, max_capacity=10)
        #      )
        empl_table = aws_dynamodb.TableV2(
            self, 
            "EmployeeTable",
            partition_key=aws_dynamodb.Attribute(
                name="id",
                type=aws_dynamodb.AttributeType.STRING
            ),
            billing=aws_dynamodb.Billing.on_demand(),
            # RemovalPolicy controls what happens to the table when the stack is destroyed:
            # - RemovalPolicy.RETAIN (default): table is kept, must be deleted manually.
            # - RemovalPolicy.DESTROY: table is deleted along with the stack.
            # - RemovalPolicy.SNAPSHOT: unsupported for DynamoDB (only for RDS/Redshift).
            removal_policy=RemovalPolicy.DESTROY,  # safe for dev; use RETAIN in production
        )

        empl_lambda = aws_lambda.Function(
            self, 
            "EmployeeLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            code=aws_lambda.Code.from_asset("services"),
            handler="index.handler",
            environment={
                "TABLE_NAME": empl_table.table_name
            }
        )
        
        # Grant the Lambda function read/write permissions to the DynamoDB table
        empl_table.grant_read_write_data(empl_lambda)

        # Create API Gateway REST API and integrate it with the Lambda function
        api = aws_apigateway.RestApi(self, "EmployeeApi")
        cors_options = aws_apigateway.CorsOptions(
            allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
            allow_methods=aws_apigateway.Cors.ALL_METHODS
        )
        empl_resource = api.root.add_resource(
            "employee", default_cors_preflight_options=cors_options)

        empl_lambda_integration = aws_apigateway.LambdaIntegration(empl_lambda)
        empl_resource.add_method("GET", empl_lambda_integration)
        empl_resource.add_method("POST", empl_lambda_integration)