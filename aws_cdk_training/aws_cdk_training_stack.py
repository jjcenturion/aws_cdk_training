from aws_cdk import (
    Stack,
    aws_s3 as s3,
    Duration,
    Fn
)
from constructs import Construct

class AwsCdkTrainingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        suffix = self.__initialize_suffix()
        # Create an S3 bucket
        self._bucket = s3.Bucket(self, "PyBucket", 
            bucket_name=Fn.join("", ["py-bucket-", suffix]),
            lifecycle_rules=[
            s3.LifecycleRule(
                expiration=Duration.days(3)
            )
        ])

    def __initialize_suffix(self):
        short_stack_id = Fn.select(2, Fn.split("/", self.stack_id))
        suffix = Fn.select(4, Fn.split("-", short_stack_id))
        return suffix
    
    @property
    def bucket(self):
        return self._bucket