# ec2_stack.py
# ------------------------------------------------------------
# Task 3 - Part 1
# EC2 stack to create an Ubuntu backend instance
# This EC2 will later be connected to API Gateway (HTTP API)
# ------------------------------------------------------------

from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
)
from constructs import Construct


class Ec2Stack(Stack):
    """
    Ec2Stack creates a simple Ubuntu EC2 instance
    that acts as a backend service for API Gateway.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ------------------------------------------------------------
        # 1. Use default VPC
        # ------------------------------------------------------------
        # Why:
        # - Fast setup
        # - No custom networking required for early stage
        # - Manager explicitly said: keep it simple
        vpc = ec2.Vpc.from_lookup(
            self,
            "DefaultVPC",
            is_default=True
        )

        # ------------------------------------------------------------
        # 2. Security Group
        # ------------------------------------------------------------
        # Controls who can talk to this EC2
        security_group = ec2.SecurityGroup(
            self,
            "BackendSecurityGroup",
            vpc=vpc,
            description="Allow HTTP and SSH access",
            allow_all_outbound=True
        )

        # Allow HTTP (for API Gateway → EC2)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic"
        )

        # Allow SSH (temporary – for debugging)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="Allow SSH access"
        )

        # ------------------------------------------------------------
        # 3. Ubuntu AMI
        # ------------------------------------------------------------
        # Latest Ubuntu 22.04 LTS (stable & production friendly)
        ubuntu_ami = ec2.MachineImage.latest_amazon_linux2023()

        # ------------------------------------------------------------
        # 4. EC2 Instance
        # ------------------------------------------------------------
        self.instance = ec2.Instance(
            self,
            "BackendInstance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ubuntu_ami,
            vpc=vpc,
            security_group=security_group,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )

        # ------------------------------------------------------------
        # 5. User Data (boot-time commands)
        # ------------------------------------------------------------
        # This installs a simple HTTP server so EC2 responds to requests
        self.instance.add_user_data(
            "#!/bin/bash",
            "yum update -y",
            "yum install -y python3",
            "echo 'Hello from EC2 backend' > index.html",
            "nohup python3 -m http.server 80 &"
        )

        # ------------------------------------------------------------
        # 6. Outputs
        # ------------------------------------------------------------
        CfnOutput(
            self,
            "Ec2PublicIp",
            value=self.instance.instance_public_ip,
            description="Public IP of the backend EC2 instance"
        )
