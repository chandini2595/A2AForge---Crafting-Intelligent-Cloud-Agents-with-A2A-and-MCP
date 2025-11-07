import json
import re
from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.ec2_agent import EC2Agent
from agents.s3_agent import S3Agent
from agents.fast_perplexity_client import FastPerplexityClient

class CoordinatorAgent(BaseAgent):
    """Main coordinator that routes requests to specialized agents with A2A"""
    
    def __init__(self):
        super().__init__("CoordinatorAgent")
        self.ec2_agent = EC2Agent()
        self.s3_agent = S3Agent()
        self.perplexity = FastPerplexityClient()  # Use fast client for low latency
        
        # Setup A2A communication network
        self._setup_a2a_network()
    
    def _setup_a2a_network(self):
        """Setup Agent-to-Agent communication network"""
        # Register all agents with each other
        self.register_agent(self.ec2_agent)
        self.register_agent(self.s3_agent)
        
        self.ec2_agent.register_agent(self)
        self.ec2_agent.register_agent(self.s3_agent)
        
        self.s3_agent.register_agent(self)
        self.s3_agent.register_agent(self.ec2_agent)
        
        print("[A2A] Agent network initialized: Coordinator ⟷ EC2Agent ⟷ S3Agent")
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process user request and route to appropriate agent"""
        
        # Always use Perplexity AI for intent understanding
        print(f"[Coordinator] Processing: {user_input}")
        intent = self.perplexity.parse_intent(user_input)
        print(f"[Coordinator] Intent: {intent}")
        
        if intent['service'] == 'ec2':
            return self._handle_ec2_action(intent, user_input)
        elif intent['service'] == 's3':
            return self._handle_s3_action(intent, user_input)
        elif intent['service'] == 'unknown':
            return self._handle_unknown(user_input, intent)
        
        # Should rarely reach here
        return {"message": "I'm not sure how to help with that. Try 'help' for available commands."}
    
    def _handle_ec2_action(self, intent: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Handle EC2 actions based on parsed intent with A2A"""
        action = intent['action']
        params = intent.get('parameters', {})
        
        if action == 'create_instance':
            # Get parameters from LLM parsing (no manual extraction needed!)
            instance_type = params.get('instance_type', 't2.micro')
            region = params.get('region')  # LLM extracts this
            
            # A2A: Check with S3 agent if user has buckets (for context)
            s3_info = self.query_agent("S3Agent", "How many buckets does user have?")
            
            result = self.ec2_agent.create_instance(instance_type=instance_type, region=region)
            
            # Add helpful context if they have S3 buckets
            if s3_info and s3_info.get('count', 0) > 0:
                result['tip'] = f"💡 You have {s3_info['count']} S3 bucket(s). You can use them with this instance!"
            
            return result
        
        elif action == 'list_instances':
            # Use A2A to get instance list
            return self.send_message("EC2Agent", {"action": "list_instances"}, "request")
        
        elif action == 'stop_instance':
            instance_id = params.get('instance_id') or self._extract_instance_id(user_input)
            if instance_id:
                return self.ec2_agent.stop_instance(instance_id)
            return {"error": "Please provide instance ID"}
        
        elif action == 'terminate_instance':
            instance_id = params.get('instance_id') or self._extract_instance_id(user_input)
            if instance_id:
                return self.ec2_agent.terminate_instance(instance_id)
            return {"error": "Please provide instance ID"}
        
        return {"error": f"Unknown EC2 action: {action}"}
    
    def _handle_s3_action(self, intent: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Handle S3 actions based on parsed intent with A2A"""
        action = intent['action']
        params = intent.get('parameters', {})
        
        if action == 'create_bucket':
            # Get parameters from LLM parsing
            bucket_name = params.get('bucket_name')
            if not bucket_name:
                return {"error": "Please provide a bucket name. Example: 'create s3 bucket my-bucket-name'"}
            region = params.get('region')  # LLM extracts this
            
            # A2A: Check with EC2 agent if user has instances
            ec2_info = self.query_agent("EC2Agent", "How many instances does user have?")
            
            result = self.s3_agent.create_bucket(bucket_name, region)
            
            # Add helpful context if they have EC2 instances
            if ec2_info and ec2_info.get('count', 0) > 0:
                result['tip'] = f"💡 You have {ec2_info['count']} EC2 instance(s). You can access this bucket from them!"
            
            return result
        
        elif action == 'list_buckets':
            # Use A2A to get bucket list
            return self.send_message("S3Agent", {"action": "list_buckets"}, "request")
        
        elif action == 'list_objects':
            bucket_name = params.get('bucket_name') or self._extract_bucket_name(user_input)
            if bucket_name:
                return self.s3_agent.list_objects(bucket_name)
            return {"error": "Please provide bucket name"}
        
        elif action == 'delete_bucket':
            bucket_name = params.get('bucket_name') or self._extract_bucket_name(user_input)
            if bucket_name:
                return self.s3_agent.delete_bucket(bucket_name)
            return {"error": "Please provide bucket name"}
        
        return {"error": f"Unknown S3 action: {action}"}
    
    def _handle_unknown(self, user_input: str, intent: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle unknown commands with AI-powered response"""
        action = intent.get('action', '') if intent else ''
        
        # Handle greetings and help
        if action in ['greeting', 'help']:
            response = self.perplexity.get_smart_response(user_input)
            return {"message": response, "greeting": True}
        
        # For other unknown commands, try to be helpful
        response = self.perplexity.get_smart_response(user_input)
        return {"message": response}
    
    def _legacy_process(self, user_input: str) -> Dict[str, Any]:
        """Original processing logic as fallback"""
        user_input_lower = user_input.lower()
        
        # Remove polite words to better parse intent
        polite_words = ['can you', 'could you', 'please', 'would you', 'can i', 'i want to', 'i need to', 'i would like to']
        for word in polite_words:
            user_input_lower = user_input_lower.replace(word, '')
        
        # EC2 Operations
        if 'ec2' in user_input_lower or 'instance' in user_input_lower:
            if 'create' in user_input_lower or 'launch' in user_input_lower:
                return self._handle_ec2_create(user_input)
            elif 'list' in user_input_lower or 'show' in user_input_lower:
                return self.ec2_agent.list_instances()
            elif 'stop' in user_input_lower:
                instance_id = self._extract_instance_id(user_input)
                if instance_id:
                    return self.ec2_agent.stop_instance(instance_id)
                return {"error": "Please provide instance ID"}
            elif 'terminate' in user_input_lower or 'delete' in user_input_lower:
                instance_id = self._extract_instance_id(user_input)
                if instance_id:
                    return self.ec2_agent.terminate_instance(instance_id)
                return {"error": "Please provide instance ID"}
        
        # S3 Operations
        elif 's3' in user_input_lower or 'bucket' in user_input_lower:
            if 'create' in user_input_lower:
                return self._handle_s3_create(user_input)
            elif 'list' in user_input_lower or 'show' in user_input_lower:
                if 'object' in user_input_lower or 'file' in user_input_lower:
                    bucket_name = self._extract_bucket_name(user_input)
                    if bucket_name:
                        return self.s3_agent.list_objects(bucket_name)
                    return {"error": "Please provide bucket name"}
                return self.s3_agent.list_buckets()
            elif 'delete' in user_input_lower:
                bucket_name = self._extract_bucket_name(user_input)
                if bucket_name:
                    return self.s3_agent.delete_bucket(bucket_name)
                return {"error": "Please provide bucket name"}
        
        return {
            "message": "I can help you with:\n"
                      "- EC2: 'create ec2 instance', 'list instances', 'stop instance <id>', 'terminate instance <id>'\n"
                      "- S3: 'create s3 bucket <name>', 'list buckets', 'delete bucket <name>', 'list objects in <bucket>'"
        }
    
    def _handle_ec2_create(self, user_input: str) -> Dict[str, Any]:
        """Handle EC2 instance creation"""
        instance_type = "t2.micro"  # default
        
        # Extract instance type if specified
        type_match = re.search(r't[2-3]\.(micro|small|medium|large)', user_input.lower())
        if type_match:
            instance_type = type_match.group(0)
        
        return self.ec2_agent.create_instance(instance_type=instance_type)
    
    def _handle_s3_create(self, user_input: str) -> Dict[str, Any]:
        """Handle S3 bucket creation"""
        bucket_name = self._extract_bucket_name(user_input)
        
        if not bucket_name:
            return {"error": "Please provide a bucket name. Example: 'create s3 bucket my-bucket-name'"}
        
        # Extract region if specified
        region = None
        region_match = re.search(r'(us|eu|ap)-(east|west|south|central|northeast|southeast)-[1-3]', user_input.lower())
        if region_match:
            region = region_match.group(0)
        
        return self.s3_agent.create_bucket(bucket_name, region)
    
    def _extract_instance_id(self, text: str) -> str:
        """Extract EC2 instance ID from text"""
        match = re.search(r'i-[a-f0-9]{8,17}', text)
        return match.group(0) if match else None
    
    def _extract_bucket_name(self, text: str) -> str:
        """Extract S3 bucket name from text"""
        # Look for bucket name after keywords
        patterns = [
            r'bucket\s+([a-z0-9][a-z0-9\-]{1,61}[a-z0-9])',
            r'in\s+([a-z0-9][a-z0-9\-]{1,61}[a-z0-9])',
            r'named?\s+([a-z0-9][a-z0-9\-]{1,61}[a-z0-9])'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1)
        
        return None
    
    def _extract_instance_type(self, text: str) -> str:
        """Extract EC2 instance type from text"""
        type_match = re.search(r't[2-3]\.(micro|small|medium|large|xlarge)', text.lower())
        return type_match.group(0) if type_match else "t2.micro"
    
    def _extract_region(self, text: str) -> str:
        """Extract AWS region from text"""
        text_lower = text.lower()
        
        # Check for explicit region codes
        region_match = re.search(r'(us|eu|ap|ca|sa)-(east|west|south|central|north|northeast|southeast)-[1-3]', text_lower)
        if region_match:
            return region_match.group(0)
        
        # Check for location names
        location_keywords = [
            'virginia', 'ohio', 'california', 'oregon',
            'ireland', 'london', 'paris', 'frankfurt', 'stockholm',
            'tokyo', 'seoul', 'osaka', 'singapore', 'sydney', 'mumbai',
            'canada', 'brazil', 'sao paulo'
        ]
        
        for keyword in location_keywords:
            if keyword in text_lower:
                return keyword
        
        # Check for "in <location>" pattern
        in_match = re.search(r'\bin\s+([a-z\s]+?)(?:\s|$)', text_lower)
        if in_match:
            location = in_match.group(1).strip()
            if location in location_keywords:
                return location
        
        return None
