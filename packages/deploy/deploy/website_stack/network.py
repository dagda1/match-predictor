from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct

class Network(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.vpc = ec2.Vpc.from_lookup(self, "DefaultVpc", is_default=True)

        cloudfront_prefix = ec2.PrefixList.from_lookup(self, "CloudFrontPrefix",
            prefix_list_name="com.amazonaws.global.cloudfront.origin-facing",
        )

        self.alb_sg = ec2.SecurityGroup(self, "AlbSg", vpc=self.vpc)
        self.alb_sg.add_ingress_rule(
            peer=ec2.Peer.prefix_list(cloudfront_prefix.prefix_list_id),
            connection=ec2.Port.tcp(80),
        )

        self.task_sg = ec2.SecurityGroup(self, "TaskSg", vpc=self.vpc)
        self.task_sg.add_ingress_rule(
            peer=self.alb_sg,
            connection=ec2.Port.tcp(3000),
        )
