from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class WebsiteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.vpc = ec2.Vpc.from_lookup(self, "DefaultVpc", is_default=True)
