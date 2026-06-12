import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_py_rest_api.cdk_py_rest_api_stack import CdkPyRestApiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_py_rest_api/cdk_py_rest_api_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkPyRestApiStack(app, "cdk-py-rest-api")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
