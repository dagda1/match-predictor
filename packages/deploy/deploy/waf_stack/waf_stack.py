from aws_cdk import Stack
from constructs import Construct

from deploy.waf_stack.waf import Waf


class WafStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        waf = Waf(self, "Waf")
        self.web_acl_arn = waf.web_acl.attr_arn
