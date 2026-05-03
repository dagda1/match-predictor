from aws_cdk import (
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_efs as efs,
)
from constructs import Construct


class ModelStorage(Construct):
    MOUNT_PATH = "/mnt/model"
    ACCESS_POINT_PATH = "/model"
    POSIX_USER = "1000"

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        lambda_security_group: ec2.SecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        self.security_group = ec2.SecurityGroup(
            self, "EfsSecurityGroup",
            vpc=vpc,
            description="Allow Lambda access to EFS for model storage",
        )

        self.security_group.add_ingress_rule(
            peer=lambda_security_group,
            connection=ec2.Port.tcp(2049),
            description="Allow NFS from Lambda",
        )

        self.file_system = efs.FileSystem(
            self, "ModelFileSystem",
            vpc=vpc,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=efs.ThroughputMode.BURSTING,
            lifecycle_policy=efs.LifecyclePolicy.AFTER_30_DAYS,
            removal_policy=RemovalPolicy.DESTROY,
            security_group=self.security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        self.access_point = self.file_system.add_access_point(
            "ModelAccessPoint",
            path=self.ACCESS_POINT_PATH,
            create_acl=efs.Acl(
                owner_uid=self.POSIX_USER,
                owner_gid=self.POSIX_USER,
                permissions="755",
            ),
            posix_user=efs.PosixUser(
                uid=self.POSIX_USER,
                gid=self.POSIX_USER,
            ),
        )

    def lambda_file_system(self) -> "lambda_.FileSystem":
        from aws_cdk import aws_lambda as lambda_
        return lambda_.FileSystem.from_efs_access_point(self.access_point, self.MOUNT_PATH)
