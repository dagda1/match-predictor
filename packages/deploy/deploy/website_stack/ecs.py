from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elbv2,
)

class Ecs(Construct):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, task_sg: ec2.SecurityGroup, target_group: elbv2.ApplicationTargetGroup, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)

        repo = ecr.Repository.from_repository_name(self, "Repo", "website_server")

        task_def = ecs.FargateTaskDefinition(self, "TaskDef", cpu=1024, memory_limit_mib=2048)
        task_def.add_container("Web",
            image=ecs.ContainerImage.from_ecr_repository(repo, "latest"),
            port_mappings=[ecs.PortMapping(container_port=3000)],
            logging=ecs.LogDriver.aws_logs(stream_prefix="website"),
        )

        self.service = ecs.FargateService(self, "Service",
            cluster=cluster,
            task_definition=task_def,
            desired_count=1,
            security_groups=[task_sg],
            assign_public_ip=True,
        )
        self.service.attach_to_application_target_group(target_group)
