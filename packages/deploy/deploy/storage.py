from aws_cdk import Stack, aws_iam as iam
from constructs import Construct

class Storage(Construct):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)