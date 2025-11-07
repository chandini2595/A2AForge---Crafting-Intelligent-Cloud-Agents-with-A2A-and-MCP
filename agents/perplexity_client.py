"""
Perplexity AI Client for enhanced natural language understanding
"""
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class PerplexityClient:
    """Client for Perplexity AI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        # Valid Perplexity models: sonar, sonar-pro, sonar-reasoning
        self.model = "sonar"  # Fast and efficient model
        
        # Cache for parsed intents (reduces API calls)
        self.intent_cache = {}
        self.cache_enabled = True
        
        if self.api_key:
            print(f"[Perplexity] Initialized with API key: {self.api_key[:10]}...")
        else:
            print("[Perplexity] WARNING: No API key found! Using fallback parsing.")
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Use Perplexity to parse user intent and extract parameters
        Uses caching for faster responses on repeated queries
        """
        # Check cache first for instant response
        cache_key = user_input.lower().strip()
        if self.cache_enabled and cache_key in self.intent_cache:
            print(f"[Perplexity] ⚡ Cache hit! Instant response")
            return self.intent_cache[cache_key]
        
        if not self.api_key:
            return self._fallback_parse(user_input)
        
        system_prompt = """You are an AWS command parser. Extract the intent and parameters from user commands.

Available operations:
- EC2: create_instance, list_instances, stop_instance, terminate_instance
- S3: create_bucket, list_buckets, delete_bucket, list_objects, upload_file

Respond ONLY with valid JSON in this format:
{
    "service": "ec2" or "s3" or "unknown",
    "action": "action_name",
    "parameters": {
        "param_name": "value"
    }
}

Parameter extraction rules:
- instance_type: t2.micro, t2.small, t2.medium, etc.
- region: Extract location names (Virginia, Ohio, Tokyo, etc.) or region codes (us-east-1, etc.)
- instance_id: i-xxxxx format
- bucket_name: lowercase with hyphens

Examples:
- "create an ec2 instance" -> {"service": "ec2", "action": "create_instance", "parameters": {}}
- "create t2.small instance in Virginia" -> {"service": "ec2", "action": "create_instance", "parameters": {"instance_type": "t2.small", "region": "virginia"}}
- "Can you create an EC2 instance in Ohio" -> {"service": "ec2", "action": "create_instance", "parameters": {"region": "ohio"}}
- "list my buckets" -> {"service": "s3", "action": "list_buckets", "parameters": {}}
- "stop instance i-123abc" -> {"service": "ec2", "action": "stop_instance", "parameters": {"instance_id": "i-123abc"}}
- "create bucket my-test-bucket in us-west-2" -> {"service": "s3", "action": "create_bucket", "parameters": {"bucket_name": "my-test-bucket", "region": "us-west-2"}}
- "hi" -> {"service": "unknown", "action": "greeting", "parameters": {}}
- "help" -> {"service": "unknown", "action": "help", "parameters": {}}
"""
        
        print(f"[Perplexity] Parsing: '{user_input}'")
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.0,  # Lower = faster, more deterministic
                "max_tokens": 150,   # Reduced for faster response
                "top_p": 0.9
            }
            
            print(f"[Perplexity] Calling API...")
            
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )
            
            print(f"[Perplexity] Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"[Perplexity] Raw response: {content}")
                
                # Extract JSON from response
                import json
                import re
                
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    print(f"[Perplexity] ✅ Parsed successfully: {parsed}")
                    
                    # Cache the result for future use
                    if self.cache_enabled:
                        self.intent_cache[cache_key] = parsed
                        print(f"[Perplexity] 💾 Cached for future requests")
                    
                    return parsed
                else:
                    print(f"[Perplexity] ❌ No JSON found in response")
            else:
                error_text = response.text
                print(f"[Perplexity] ❌ API error {response.status_code}: {error_text}")
            
            print("[Perplexity] Falling back to manual parsing")
            return self._fallback_parse(user_input)
            
        except Exception as e:
            print(f"[Perplexity] ❌ Exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_parse(user_input)
    
    def _fallback_parse(self, user_input: str) -> Dict[str, Any]:
        """Fallback parsing without AI"""
        user_input_lower = user_input.lower()
        
        # Check for EC2/S3 operations first (before greetings)
        # This ensures "Can you create an EC2 instance" is parsed correctly
        if 'ec2' in user_input_lower or 'instance' in user_input_lower:
            if 'create' in user_input_lower or 'launch' in user_input_lower:
                return {"service": "ec2", "action": "create_instance", "parameters": {}}
            elif 'list' in user_input_lower or 'show' in user_input_lower:
                return {"service": "ec2", "action": "list_instances", "parameters": {}}
            elif 'stop' in user_input_lower:
                return {"service": "ec2", "action": "stop_instance", "parameters": {}}
            elif 'terminate' in user_input_lower or 'delete' in user_input_lower:
                return {"service": "ec2", "action": "terminate_instance", "parameters": {}}
        
        elif 's3' in user_input_lower or 'bucket' in user_input_lower:
            if 'create' in user_input_lower:
                return {"service": "s3", "action": "create_bucket", "parameters": {}}
            elif 'list' in user_input_lower:
                if 'object' in user_input_lower or 'file' in user_input_lower:
                    return {"service": "s3", "action": "list_objects", "parameters": {}}
                return {"service": "s3", "action": "list_buckets", "parameters": {}}
            elif 'delete' in user_input_lower:
                return {"service": "s3", "action": "delete_bucket", "parameters": {}}
        
        # Check for greetings and general queries (after checking for operations)
        greetings = ['hi', 'hello', 'hey', 'help', 'what can you do', 'how are you']
        # Only treat as greeting if it's JUST a greeting, not part of a command
        if any(user_input_lower.strip() == greeting or user_input_lower.strip().startswith(greeting + ' ') 
               for greeting in ['hi', 'hello', 'hey', 'help']):
            if 'ec2' not in user_input_lower and 's3' not in user_input_lower and 'instance' not in user_input_lower and 'bucket' not in user_input_lower:
                return {"service": "unknown", "action": "greeting", "parameters": {}}
        
        return {"service": "unknown", "action": "help", "parameters": {}}
    
    def get_smart_response(self, user_input: str, context: str = "") -> str:
        """
        Get a conversational response from Perplexity
        """
        if not self.api_key:
            return self._get_friendly_fallback_response(user_input)
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful AWS assistant. Be concise, friendly, and enthusiastic. Use emojis occasionally."},
                        {"role": "user", "content": f"{context}\n\nUser: {user_input}"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Perplexity API error: {e}")
        
        return self._get_friendly_fallback_response(user_input)
    
    def _get_friendly_fallback_response(self, user_input: str) -> str:
        """Get a friendly response without AI"""
        user_input_lower = user_input.lower()
        
        # Greetings
        if any(word in user_input_lower for word in ['hi', 'hello', 'hey']):
            return """👋 Hi there! I'm your AWS Multi-Agent Assistant!

I can help you manage your AWS resources. What do you want me to do interesting today?

Try commands like:
  • "list my instances"
  • "create an ec2 instance"
  • "show me my s3 buckets"

Or type "help" to see everything I can do! 🚀"""
        
        # Help requests
        if any(word in user_input_lower for word in ['help', 'what can you do', 'capabilities']):
            return """🤖 Here's what I can do for you!

📦 **EC2 Commands:**
  • create ec2 instance [type]
  • list instances
  • stop instance <id>
  • terminate instance <id>

🗄️ **S3 Commands:**
  • create s3 bucket <name>
  • list buckets
  • delete bucket <name>
  • list objects in <bucket>

💡 Just use natural language - I'll understand! What would you like to try?"""
        
        # Default response
        return """Hmm, I'm not sure what you mean! 🤔

I can help you manage AWS EC2 instances and S3 buckets. Try:
  • "list my instances"
  • "create an ec2 instance"
  • "show me my buckets"

Type "help" for more options!"""
