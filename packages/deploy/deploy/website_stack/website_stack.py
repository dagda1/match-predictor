from aws_cdk import (
    Stack,
)
from constructs import Construct
from deploy.website_stack.network import Network
from deploy.website_stack.alb import Alb
from deploy.website_stack.ecs import Ecs

class WebsiteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        network = Network(self, "Network")
        alb = Alb(self, "Alb", vpc=network.vpc, alb_sg=network.alb_sg)
        Ecs(self, "Ecs", vpc=network.vpc, task_sg=network.task_sg, target_group=alb.target_group)


        
