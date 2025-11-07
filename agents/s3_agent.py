import boto3
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, Message

class S3Agent(BaseAgent):
    """Agent specialized in S3 bucket operations with A2A capabilities"""
    
    def __init__(self):
        super().__init__("S3Agent")
        self.s3 = boto3.client('s3')
        self.bucket_cache = {}
    
    def handle_message(self, message: Message) -> Any:
        """Handle A2A messages from other agents"""
        content = message.content
        
        if message.msg_type == "query":
            query = content.get("query", "")
            
            if "bucket" in query.lower() and "count" in query.lower():
                buckets = self.list_buckets()
                count = len(buckets.get("buckets", []))
                return {"count": count, "buckets": buckets}
            
            elif "storage" in query.lower() or "size" in query.lower():
                return {"message": "Storage size calculation requires CloudWatch metrics"}
        
        elif message.msg_type == "request":
            action = content.get("action")
            
            if action == "list_buckets":
                return self.list_buckets()
            elif action == "bucket_exists":
                bucket_name = content.get("bucket_name")
                return self._bucket_exists(bucket_name)
        
        return super().handle_message(message)
    
    def _bucket_exists(self, bucket_name: str) -> Dict[str, Any]:
        """Check if a bucket exists"""
        try:
            self.s3.head_bucket(Bucket=bucket_name)
            return {"exists": True, "bucket_name": bucket_name}
        except:
            return {"exists": False, "bucket_name": bucket_name}
    
    def create_bucket(self, bucket_name: str, region: str = None) -> Dict[str, Any]:
        """Create an S3 bucket"""
        try:
            # Get the current region from the client if not specified
            if not region:
                region = self.s3.meta.region_name
            
            # us-east-1 doesn't need LocationConstraint, all others do
            if region == 'us-east-1':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            return {
                "success": True,
                "bucket_name": bucket_name,
                "region": region,
                "message": f"S3 bucket '{bucket_name}' created successfully in {region}"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def list_buckets(self) -> Dict[str, Any]:
        """List all S3 buckets"""
        try:
            response = self.s3.list_buckets()
            buckets = [
                {
                    'name': bucket['Name'],
                    'creation_date': str(bucket['CreationDate'])
                }
                for bucket in response['Buckets']
            ]
            return {"success": True, "buckets": buckets}
        except Exception as e:
            return {"error": str(e)}
    
    def delete_bucket(self, bucket_name: str, force: bool = False) -> Dict[str, Any]:
        """Delete an S3 bucket"""
        try:
            if force:
                # Delete all objects first
                response = self.s3.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in response:
                    for obj in response['Contents']:
                        self.s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
            
            self.s3.delete_bucket(Bucket=bucket_name)
            return {
                "success": True,
                "bucket_name": bucket_name,
                "message": f"S3 bucket '{bucket_name}' deleted successfully"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def upload_file(self, bucket_name: str, file_path: str, object_name: str = None) -> Dict[str, Any]:
        """Upload a file to S3 bucket"""
        try:
            if object_name is None:
                object_name = file_path.split('/')[-1]
            
            self.s3.upload_file(file_path, bucket_name, object_name)
            return {
                "success": True,
                "bucket_name": bucket_name,
                "object_name": object_name,
                "message": f"File uploaded to '{bucket_name}/{object_name}'"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def list_objects(self, bucket_name: str) -> Dict[str, Any]:
        """List objects in an S3 bucket"""
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            objects = []
            if 'Contents' in response:
                objects = [
                    {
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': str(obj['LastModified'])
                    }
                    for obj in response['Contents']
                ]
            return {"success": True, "bucket_name": bucket_name, "objects": objects}
        except Exception as e:
            return {"error": str(e)}
