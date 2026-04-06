from aws_cdk import aws_certificatemanager as acm, aws_route53 as route53
from constructs import Construct

DOMAIN_NAME = "premierpredictor.co.uk"


class Certificate(Construct):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone",
            domain_name=DOMAIN_NAME,
        )

        self.certificate = acm.Certificate(self, "Certificate",
            domain_name=DOMAIN_NAME,
            validation=acm.CertificateValidation.from_dns(self.hosted_zone),
        )
