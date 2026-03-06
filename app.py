#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk_training.aws_cdk_training_stack import AwsCdkTrainingStack
from aws_cdk_training.handler_stack import HandlerStack


app = cdk.App()
started_stack = AwsCdkTrainingStack(app, "AwsCdkTrainingStack")
HandlerStack(app, "HandlerStack", bucket=started_stack.bucket)
app.synth()
