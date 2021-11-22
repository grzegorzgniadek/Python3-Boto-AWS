#!/usr/bin/python3

import boto3,argparse,sys,logging,argparse

def parser_create_ec2_instance():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-region',required=True,type=str
    )
    args.add_argument(
        '-architecture',required=True,type=str
    )
    args.add_argument(
        '-instance_name',required=True,type=str
    )
    args.add_argument(
        '-disk_size',required=True,type=int
    )
    return args.parse_args();

def parser_modifyterminate_ec2_instance():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-region',required=True,type=str
    )
    args.add_argument(
        '-instance_id',required=True,type=str
    )
    return args.parse_args();

class Utils:
    def __init__(self):
        self.init_logger()

    def init_logger(self):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('utils')

    def create_ec2_instance(self,region,architecture,instance_name,disk_size):
        region_security_group_name = self.get_security_group(region)
        region,architecture,image = self.get_last_image_ami(region, architecture)
        key_pair_name = self.get_key_pairs(region)
        subnet_id = self.get_subnet_id(region)

        self.logger.info("{}".format("Creating instance " + instance_name ))

        client = boto3.resource('ec2', region_name=region)
        instance = client.create_instances(
            BlockDeviceMappings=[
                {   
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': disk_size,
                        'VolumeType': 'gp2',
                    }
                }
            ],
            ImageId=image, 
            InstanceType = 't2.micro',  
            SubnetId=subnet_id,
            SecurityGroupIds=[region_security_group_name],
            MaxCount=1,
            MinCount=1,
            KeyName=key_pair_name,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        },
                    ]
                },
            ]
        )
        instance = instance[0]
        instance.wait_until_running()
        self.logger.info("{}".format("Creating instance " + instance_name +" done"))        
        instance.load()
        print(instance.public_ip_address)

    def get_last_image_ami(self,region,architecture):
        tab = []
        client = boto3.resource('ec2', region_name=region)
        images = client.images.filter(
            Filters=[
                {
                    'Name': 'name',
                    'Values': ['ubuntu/images/hvm-ssd/ubuntu-focal-20.04-*']
                },
                {
                    'Name': 'architecture',
                    'Values': [architecture]
                },
                {
                    'Name': 'owner-id',
                    'Values': ['099720109477']
                }
            ]
        )
        for image_name in images:
            tab.append([image_name.id,image_name.creation_date])

        tab.sort(key = lambda tab_list: tab_list[1])
        image = tab[-1][0]
        return region,architecture,image

    def get_security_group(self,region):
        
        client = boto3.client('ec2',region_name=region)
        security_group = client.describe_security_groups(
            Filters=[
                {
                    'Name': 'group-name',
                    'Values': ['aws*']
                }
            ]
        )
        region_security_group = security_group['SecurityGroups'][0]['GroupId']
        return region_security_group

    def get_key_pairs(self,region):
        
        client = boto3.client('ec2',region_name=region)
        response = client.describe_key_pairs(
            Filters=[
                {
                    'Name': 'key-name',
                    'Values': [
                        'jenkins*',
                    ]
                },
            ],
        )
        key_pair = response['KeyPairs'][0]['KeyName']
        return key_pair

    def get_subnet_id(self,region):
        
        client = boto3.client('ec2',region)
        response = client.describe_subnets(
            Filters=[
                {
                    'Name': 'cidr-block',
                    'Values': [
                        '172.31.32*',
                    ]
                },
            ],
        )
        subnet_id = response['Subnets'][0]['SubnetId']
        return subnet_id


    def terminate_ec2_instance(self,region,instance_id):
    
        client = boto3.client('ec2', region_name=region)
        instance = client.terminate_instances(
            InstanceIds=[instance_id]
        )
        self.logger.info("{}".format("Terminating instance: " + instance_id + "done" ))

    def modify_ec2_instance(self,region,instance_id):
        
        client = boto3.client('ec2', region_name=region)
        response = client.modify_instance_attribute(

            DisableApiTermination={
                'Value': False
            },
            InstanceId=instance_id
        )
        self.logger.info("{}".format("Modifying instance: " + instance_id + "done" ))


