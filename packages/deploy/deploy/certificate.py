from aws_cdk import (
    Stack,
    aws_certificatemanager as acm,
    aws_route53 as route53,
)
from constructs import Construct

DOMAIN_NAME = "premierpredictor.co.uk"


class CertificateStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone",
            domain_name=DOMAIN_NAME,
        )

        self.certificate = acm.Certificate(self, "Certificate",
            domain_name=DOMAIN_NAME,
            validation=acm.CertificateValidation.from_dns(self.hosted_zone),
        )
