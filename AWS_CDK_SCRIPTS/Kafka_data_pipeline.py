from aws_cdk import core
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_msk as msk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_secretsmanager as secretsmanager
import os

# Components:
#    - AWS secrets manager
#    - VPC
#    - EC2 client security/ssh setup
#    - MSK for kafka cluster
#    - IAM

#NOTE: restrict ssh ip range prior to deployment. See ingress_rule note.


class KafkaSetupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        secret_name = os.environ.get('EC2_KEY_PAIR_SECRET_NAME')

        if not secret_name:
            raise ValueError("env var EC2_KEY_PAIR_SECRET_NAME not set")



        key_pair_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "KeyPairSecret", 
            secret_name  
        )

        # VPC
        vpc = ec2.Vpc(self, "KafkaVPC",
                      max_azs=3  # Default is all AZs in the region
                      )

        # EC2 client security   
        ec2_sg = ec2.SecurityGroup(self, "EC2SecurityGroup",
                                   vpc=vpc,
                                   description="Allow SSH access",
                                   allow_all_outbound=True)

        # NOTE: At deployment restrict access to specific IP range, or single address 
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH access from anywhere")

        # ip_addr = "<insert address>/32"
        # ec2_sg.add_ingress_rule(ec2.Peer.ipv4(ip_addr), ec2.Port.tcp(22), "Allow SSH access only from my IP")



        #  MSK cluster
        msk_cluster = msk.CfnCluster(self, "KafkaCluster",
                                     cluster_name="KafkaCluster",
                                     kafka_version="2.6.1",
                                     number_of_broker_nodes=3,
                                     broker_node_group_info={
                                         "instanceType": "kafka.m5.large",
                                         "brokerAzDistribution": "DEFAULT",
                                         "storageInfo": {
                                             "ebsStorageInfo": {
                                                 "volumeSize": 1000  # 1000 GiB
                                             }
                                         },
                                         "clientSubnets": vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnet_ids,
                                         "securityGroups": [vpc.vpc_default_security_group]
                                     }
                                     )

        # IAM for EC2 intances 
        role = iam.Role(self, "KafkaClientRole",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                        managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonMSKReadOnlyAccess")]
                        )

        # EC2 instances: kafka clients
        for i in range(1, 4):
            ec2.Instance(self, f"KafkaClient{i}",
                         instance_type=ec2.InstanceType("t3.small"),
                         machine_image=ec2.MachineImage.latest_amazon_linux(),
                         vpc=vpc,
                         role=role,
                         vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                         key_name=key_pair_secret.secret_value.to_string()
                         )

app = core.App()
KafkaSetupStack(app, "KafkaSetupStack")
app.synth()

