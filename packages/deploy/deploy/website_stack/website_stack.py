from aws_cdk import (
    Stack,
)
from constructs import Construct
from deploy.website_stack.s3 import Storage
from deploy.website_stack.cdn import Cdn

class WebsiteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        storage = Storage(self, "Storage")
        Cdn(self, "Cdn", bucket=storage.bucket)


        
