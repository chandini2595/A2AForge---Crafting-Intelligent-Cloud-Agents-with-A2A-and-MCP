import boto3
from typing import Dict, Any
from agents.base_agent import BaseAgent, Message

class EC2Agent(BaseAgent):
    """Agent specialized in EC2 instance operations with A2A capabilities"""
    
    def __init__(self):
        super().__init__("EC2Agent")
        self.ec2 = boto3.client('ec2')
        self.ec2_resource = boto3.resource('ec2')
        self.instance_cache = {}
    
    def handle_message(self, message: Message) -> Any:
        """Handle A2A messages from other agents"""
        content = message.content
        
        if message.msg_type == "query":
            query = content.get("query", "")
            
            if "instance" in query.lower() and "count" in query.lower():
                instances = self.list_instances()
                count = len(instances.get("instances", []))
                return {"count": count, "instances": instances}
            
            elif "running" in query.lower():
                instances = self.list_instances()
                running = [i for i in instances.get("instances", []) 
                          if i.get("state") == "running"]
                return {"running_count": len(running), "instances": running}
        
        elif message.msg_type == "request":
            action = content.get("action")
            
            if action == "list_instances":
                return self.list_instances()
            elif action == "get_instance_info":
                instance_id = content.get("instance_id")
                return self._get_instance_info(instance_id)
        
        return super().handle_message(message)
    
    def _get_instance_info(self, instance_id: str) -> Dict[str, Any]:
        """Get detailed info about a specific instance"""
        try:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                return {
                    "success": True,
                    "instance_id": instance_id,
                    "state": instance['State']['Name'],
                    "type": instance['InstanceType'],
                    "launch_time": str(instance['LaunchTime'])
                }
        except Exception as e:
            return {"error": str(e)}
        return {"error": "Instance not found"}
    
    def create_instance(self, instance_type: str = "t2.micro", 
                       ami_id: str = None, 
                       key_name: str = None,
                       tags: Dict[str, str] = None,
                       region: str = None) -> Dict[str, Any]:
        """Create an EC2 instance in specified region"""
        try:
            # Map region name to AWS region code
            target_region = self._map_region(region) if region else "us-east-2"
            
            # Create EC2 client for target region
            ec2_client = boto3.client('ec2', region_name=target_region)
            ec2_resource = boto3.resource('ec2', region_name=target_region)
            # Get default AMI if not provided
            if not ami_id:
                # Try Amazon Linux 2023 first, then fall back to Amazon Linux 2
                ami_patterns = [
                    'al2023-ami-*-x86_64',  # Amazon Linux 2023
                    'amzn2-ami-hvm-*-x86_64-gp2',  # Amazon Linux 2
                    'ubuntu/images/hvm-ssd/ubuntu-*-amd64-server-*'  # Ubuntu fallback
                ]
                
                for pattern in ami_patterns:
                    try:
                        response = ec2_client.describe_images(
                            Owners=['amazon'],
                            Filters=[
                                {'Name': 'name', 'Values': [pattern]},
                                {'Name': 'state', 'Values': ['available']},
                                {'Name': 'architecture', 'Values': ['x86_64']}
                            ],
                            MaxResults=5
                        )
                        if response['Images']:
                            images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
                            ami_id = images[0]['ImageId']
                            break
                    except:
                        continue
            
            if not ami_id:
                # Fallback to common AMI IDs by region
                fallback_amis = {
                    'us-east-1': 'ami-0c55b159cbfafe1f0',  # Amazon Linux 2
                    'us-east-2': 'ami-0c55b159cbfafe1f0',  # Amazon Linux 2
                    'us-west-1': 'ami-0d1cd67c26f5fca19',
                    'us-west-2': 'ami-0d1cd67c26f5fca19',
                    'eu-west-1': 'ami-0d71ea30463e0ff8d',
                    'eu-west-2': 'ami-0d71ea30463e0ff8d',
                    'ap-southeast-1': 'ami-0c802847a7dd848c0'
                }
                ami_id = fallback_amis.get(target_region)
                
                if not ami_id:
                    return {"error": f"No AMI found for region {target_region}. Please specify ami_id parameter."}
            
            params = {
                'ImageId': ami_id,
                'InstanceType': instance_type,
                'MinCount': 1,
                'MaxCount': 1
            }
            
            if key_name:
                params['KeyName'] = key_name
            
            if tags:
                params['TagSpecifications'] = [{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': k, 'Value': v} for k, v in tags.items()]
                }]
            
            instances = ec2_resource.create_instances(**params)
            instance = instances[0]
            
            # Wait for instance to be running
            instance.wait_until_running()
            instance.reload()  # Refresh instance data
            
            # Get region name for display
            region_name = self._get_region_name(target_region)
            
            return {
                "success": True,
                "instance_id": instance.id,
                "instance_type": instance_type,
                "ami_id": ami_id,
                "region": target_region,
                "region_name": region_name,
                "state": instance.state['Name'],
                "message": f"EC2 instance {instance.id} created successfully in {region_name} ({target_region})"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def list_instances(self) -> Dict[str, Any]:
        """List all EC2 instances"""
        try:
            response = self.ec2.describe_instances()
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': str(instance['LaunchTime'])
                    })
            return {"success": True, "instances": instances}
        except Exception as e:
            return {"error": str(e)}
    
    def stop_instance(self, instance_id: str) -> Dict[str, Any]:
        """Stop an EC2 instance - searches all regions"""
        try:
            # First, find which region the instance is in
            instance_region = self._find_instance_region(instance_id)
            
            if not instance_region:
                return {"error": f"Instance {instance_id} not found in any region"}
            
            # Create clients for the correct region
            ec2_client = boto3.client('ec2', region_name=instance_region)
            ec2_resource = boto3.resource('ec2', region_name=instance_region)
            
            # Stop the instance
            response = ec2_client.stop_instances(InstanceIds=[instance_id])
            
            # Wait for instance to stop
            instance = ec2_resource.Instance(instance_id)
            instance.wait_until_stopped()
            
            region_name = self._get_region_name(instance_region)
            
            return {
                "success": True,
                "instance_id": instance_id,
                "region": instance_region,
                "region_name": region_name,
                "message": f"Instance {instance_id} stopped successfully in {region_name} ({instance_region})"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def terminate_instance(self, instance_id: str) -> Dict[str, Any]:
        """Terminate an EC2 instance - searches all regions"""
        try:
            # First, find which region the instance is in
            instance_region = self._find_instance_region(instance_id)
            
            if not instance_region:
                return {"error": f"Instance {instance_id} not found in any region"}
            
            # Create clients for the correct region
            ec2_client = boto3.client('ec2', region_name=instance_region)
            ec2_resource = boto3.resource('ec2', region_name=instance_region)
            
            # Terminate the instance
            response = ec2_client.terminate_instances(InstanceIds=[instance_id])
            
            # Wait for instance to terminate
            instance = ec2_resource.Instance(instance_id)
            instance.wait_until_terminated()
            
            region_name = self._get_region_name(instance_region)
            
            return {
                "success": True,
                "instance_id": instance_id,
                "region": instance_region,
                "region_name": region_name,
                "message": f"Instance {instance_id} terminated successfully in {region_name} ({instance_region})"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _map_region(self, region_input: str) -> str:
        """Map location names or region codes to AWS region codes"""
        if not region_input:
            return "us-east-2"  # Default region
        
        region_lower = region_input.lower().strip()
        
        # Region mapping dictionary
        region_map = {
            # US Regions
            'virginia': 'us-east-1',
            'n. virginia': 'us-east-1',
            'north virginia': 'us-east-1',
            'us-east-1': 'us-east-1',
            
            'ohio': 'us-east-2',
            'us-east-2': 'us-east-2',
            
            'california': 'us-west-1',
            'n. california': 'us-west-1',
            'northern california': 'us-west-1',
            'us-west-1': 'us-west-1',
            
            'oregon': 'us-west-2',
            'us-west-2': 'us-west-2',
            
            # Europe Regions
            'ireland': 'eu-west-1',
            'eu-west-1': 'eu-west-1',
            
            'london': 'eu-west-2',
            'eu-west-2': 'eu-west-2',
            
            'paris': 'eu-west-3',
            'eu-west-3': 'eu-west-3',
            
            'frankfurt': 'eu-central-1',
            'eu-central-1': 'eu-central-1',
            
            'stockholm': 'eu-north-1',
            'eu-north-1': 'eu-north-1',
            
            # Asia Pacific Regions
            'tokyo': 'ap-northeast-1',
            'ap-northeast-1': 'ap-northeast-1',
            
            'seoul': 'ap-northeast-2',
            'ap-northeast-2': 'ap-northeast-2',
            
            'osaka': 'ap-northeast-3',
            'ap-northeast-3': 'ap-northeast-3',
            
            'singapore': 'ap-southeast-1',
            'ap-southeast-1': 'ap-southeast-1',
            
            'sydney': 'ap-southeast-2',
            'ap-southeast-2': 'ap-southeast-2',
            
            'mumbai': 'ap-south-1',
            'ap-south-1': 'ap-south-1',
            
            # Canada
            'canada': 'ca-central-1',
            'central': 'ca-central-1',
            'ca-central-1': 'ca-central-1',
            
            # South America
            'sao paulo': 'sa-east-1',
            'brazil': 'sa-east-1',
            'sa-east-1': 'sa-east-1',
        }
        
        return region_map.get(region_lower, "us-east-2")
    
    def _get_region_name(self, region_code: str) -> str:
        """Get friendly name for region code"""
        region_names = {
            'us-east-1': 'N. Virginia',
            'us-east-2': 'Ohio',
            'us-west-1': 'N. California',
            'us-west-2': 'Oregon',
            'eu-west-1': 'Ireland',
            'eu-west-2': 'London',
            'eu-west-3': 'Paris',
            'eu-central-1': 'Frankfurt',
            'eu-north-1': 'Stockholm',
            'ap-northeast-1': 'Tokyo',
            'ap-northeast-2': 'Seoul',
            'ap-northeast-3': 'Osaka',
            'ap-southeast-1': 'Singapore',
            'ap-southeast-2': 'Sydney',
            'ap-south-1': 'Mumbai',
            'ca-central-1': 'Canada Central',
            'sa-east-1': 'São Paulo',
        }
        return region_names.get(region_code, region_code)
    
    def _find_instance_region(self, instance_id: str) -> str:
        """Find which region an instance is in by checking all regions"""
        print(f"[EC2Agent] 🔍 Searching for instance {instance_id} across all regions...")
        
        # Get all available regions
        ec2_client = boto3.client('ec2')
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
        
        # Search each region
        for region in regions:
            try:
                regional_client = boto3.client('ec2', region_name=region)
                response = regional_client.describe_instances(InstanceIds=[instance_id])
                
                if response['Reservations']:
                    print(f"[EC2Agent] ✅ Found instance {instance_id} in {region}")
                    return region
            except:
                # Instance not in this region, continue searching
                continue
        
        print(f"[EC2Agent] ❌ Instance {instance_id} not found in any region")
        return None
