from aws_cdk import Stack
from constructs import Construct

from deploy.certificate_stack.certificate import Certificate
from deploy.certificate_stack.waf import Waf


class EdgeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cert = Certificate(self, "Certificate")
        self.certificate = cert.certificate
        self.hosted_zone = cert.hosted_zone

        waf = Waf(self, "Waf")
        self.web_acl_arn = waf.web_acl.attr_arn
