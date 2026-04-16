from aws_cdk import (
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_rds as rds,
)
from constructs import Construct


class Database(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        security_group: ec2.SecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        self.instance = rds.DatabaseInstance(self, "Postgres",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_18_3,
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G,
                ec2.InstanceSize.MICRO,
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[security_group],
            database_name="match_predictor",
            iam_authentication=True,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
            cloudwatch_logs_retention=logs.RetentionDays.ONE_WEEK,
        )
