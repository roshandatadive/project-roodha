#!/usr/bin/env python3
import os
import aws_cdk as cdk

from ec2_stack import Ec2Stack
from api_gateway_stack import ApiGatewayStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "ap-south-1"),
)

# EC2 stack (already deployed)
ec2_stack = Ec2Stack(
    app,
    "Ec2Stack",
    env=env,
)

# API Gateway in front of EC2
ApiGatewayStack(
    app,
    "ApiGatewayStack",
    backend_url="http://13.233.80.182",
    env=env,
)

app.synth()
