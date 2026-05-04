from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class Vpc(Construct):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.vpc = ec2.Vpc(self, "Vpc",
            ip_protocol=ec2.IpProtocol.DUAL_STACK,
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

        self.s3_endpoint = self.vpc.add_gateway_endpoint("S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
        )

        self.database_security_group = ec2.SecurityGroup(self, "DatabaseSecurityGroup",
            vpc=self.vpc,
            description="Allow Lambda access to RDS",
        )

        self.lambda_security_group = ec2.SecurityGroup(self, "LambdaSecurityGroup",
            vpc=self.vpc,
            description="Security group for Lambda functions",
            allow_all_outbound=False,
        )

        self.lambda_security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic(),
            description="Allow all IPv4 outbound",
        )

        self.lambda_security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv6(),
            connection=ec2.Port.all_traffic(),
            description="Allow all IPv6 outbound",
        )

        self.database_security_group.add_ingress_rule(
            peer=self.lambda_security_group,
            connection=ec2.Port.tcp(5432),
            description="Allow Postgres access from Lambda",
        )
