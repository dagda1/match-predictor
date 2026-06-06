from constructs import Construct
from aws_cdk import (
    Duration,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
)

class Alb(Construct):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, alb_sg: ec2.SecurityGroup, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
            
        self.alb = elbv2.ApplicationLoadBalancer(self, "Lb",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_sg,
            idle_timeout=Duration.seconds(3600),
        )

        self.target_group = elbv2.ApplicationTargetGroup(self, "Tg",
            vpc=vpc,
            port=3000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(path="/"),
        )

        self.alb.add_listener("HttpListener",
            port=80,
            default_target_groups=[self.target_group],
        )
