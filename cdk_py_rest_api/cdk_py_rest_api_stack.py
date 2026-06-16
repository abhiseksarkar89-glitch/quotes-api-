from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch, Duration,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_cloudwatch_actions as snsAction,
    # aws_sqs as sqs,
)
from constructs import Construct
import os
class CdkPyRestApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table
        table = dynamodb.Table(
            self, "dyn-quotes-table",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        log_group = logs.LogGroup(
            self,
            "QuotesLambdaLogGroup",
            log_group_name=f"/aws/lambda/quotesHandlerLambda",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Lambda function
        handler_function = _lambda.Function(
            self, "quotesHandlerLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../lambdas")
            ),
            handler="quotest.handler", #fileName.functionName()
            environment={
                "MY_TABLE": table.table_name,
                "LOG_LEVEL": "DEBUG"
            }
        )

        # Lambda invocation metric
        invocation_metric = handler_function.metric_invocations(
            period = Duration.minutes(1)
        )
        # Alarm for 5 invocations
        invocation_alarm = cloudwatch.Alarm(
            self, "LambdaInvocationAlarm" ,
            metric=invocation_metric,
            threshold= 5,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
        )
        
        # Add email notification
        topic = sns.Topic(self,"AlarmTopic")
        topic.add_subscription(
            subs.EmailSubscription("abhisek.sarkar@capgemini.com")
        )
        invocation_alarm.add_alarm_action(
            snsAction.SnsAction(topic)
        )

        # IMPORTANT Permission to scan the Dynamo DB 
        table.grant_read_write_data(handler_function)





        # Create API Gateway
        api = apigateway.RestApi(
            self, "quotesPyApi",     
        )

        # Create /quotes endpoint
        quotes_resource = api.root.add_resource("myquotes")

        #  Add GET/PUT/DELETE method with Lambda integration
        quotes_resource.add_method("GET", apigateway.LambdaIntegration(handler_function))
        quotes_resource.add_method("POST", apigateway.LambdaIntegration(handler_function))
        quotes_resource.add_resource({"id"}).add_method("DELETE",apigateway.LambdaIntegration(handler_function)) 