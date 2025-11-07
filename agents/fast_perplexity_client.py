"""
Fast Perplexity Client with async support and aggressive caching
"""
import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import json
import re
from functools import lru_cache

load_dotenv()


class FastPerplexityClient:
    """Optimized Perplexity client for low latency"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar"  # Fastest model
        
        if self.api_key:
            print(f"[Perplexity] ✅ Initialized with API key: {self.api_key[:10]}...")
            print(f"[Perplexity] 🚀 Cache DISABLED - All queries go to LLM")
        else:
            print("[Perplexity] ❌ WARNING: No API key found! Using fallback parsing.")
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Parse intent - ALWAYS call LLM (NO CACHE)"""
        
        # If no API key, use fast fallback
        if not self.api_key:
            print(f"[Perplexity] ⚠️  No API key - using fallback")
            return self._fast_fallback(user_input)
        
        # ALWAYS call LLM - NO CACHING
        print(f"[Perplexity] 🤖 Calling LLM to parse: '{user_input}'")
        result = self._call_api_sync(user_input)
        
        return result
    
    def _call_api_sync(self, user_input: str) -> Dict[str, Any]:
        """Synchronous API call with minimal overhead"""
        import requests
        
        system_prompt = """You are a JSON-only AWS command parser. You MUST respond with ONLY valid JSON, nothing else.

Format (REQUIRED):
{"service": "ec2|s3|unknown", "action": "action_name", "parameters": {}}

Actions:
- EC2: create_instance, list_instances, stop_instance, terminate_instance
- S3: create_bucket, list_buckets, delete_bucket, list_objects
- Unknown: greeting, help

Parameters to extract:
- instance_type: t2.micro, t2.small, etc.
- region: Virginia→virginia, Ohio→ohio, Tokyo→tokyo, or us-east-1, etc.
- instance_id: i-xxxxx
- bucket_name: lowercase-with-hyphens

CRITICAL: Return ONLY JSON, no explanations!

Examples:
"How are you?" → {"service": "unknown", "action": "greeting", "parameters": {}}
"what is aws" → {"service": "unknown", "action": "greeting", "parameters": {}}
"create ec2 in ohio" → {"service": "ec2", "action": "create_instance", "parameters": {"region": "ohio"}}
"list instances" → {"service": "ec2", "action": "list_instances", "parameters": {}}"""
        
        print(f"[Perplexity] 📡 Making API request to Perplexity...")
        
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
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    "temperature": 0.0,
                    "max_tokens": 150,
                },
                timeout=10
            )
            
            print(f"[Perplexity] 📥 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                print(f"[Perplexity] 📄 LLM Response: {content[:200]}...")
                
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    print(f"[Perplexity] ✅ Parsed JSON: {parsed}")
                    
                    # Fix unknown action - default to greeting for conversational queries
                    if parsed.get('action') == 'unknown':
                        parsed['action'] = 'greeting'
                    
                    return parsed
                else:
                    print(f"[Perplexity] ❌ No JSON found in LLM response")
            else:
                print(f"[Perplexity] ❌ API Error: {response.text[:200]}")
        
        except Exception as e:
            print(f"[Perplexity] ❌ Exception during API call: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"[Perplexity] ⚠️  Falling back to keyword matching")
        return self._fast_fallback(user_input)
    
    def _fast_fallback(self, user_input: str) -> Dict[str, Any]:
        """Ultra-fast keyword-based fallback"""
        text = user_input.lower()
        
        # EC2 operations
        if 'ec2' in text or 'instance' in text:
            if 'create' in text or 'launch' in text:
                return {'service': 'ec2', 'action': 'create_instance', 'parameters': {}}
            elif 'list' in text or 'show' in text:
                return {'service': 'ec2', 'action': 'list_instances', 'parameters': {}}
            elif 'stop' in text:
                return {'service': 'ec2', 'action': 'stop_instance', 'parameters': {}}
            elif 'terminate' in text or 'delete' in text:
                return {'service': 'ec2', 'action': 'terminate_instance', 'parameters': {}}
        
        # S3 operations
        if 's3' in text or 'bucket' in text:
            if 'create' in text:
                return {'service': 's3', 'action': 'create_bucket', 'parameters': {}}
            elif 'list' in text:
                return {'service': 's3', 'action': 'list_buckets', 'parameters': {}}
            elif 'delete' in text:
                return {'service': 's3', 'action': 'delete_bucket', 'parameters': {}}
        
        # Greetings and conversational
        greetings = ['hi', 'hello', 'hey', 'how are you', 'how are u', 'whats up', "what's up"]
        if any(g in text for g in greetings):
            return {'service': 'unknown', 'action': 'greeting', 'parameters': {}}
        
        if 'help' in text:
            return {'service': 'unknown', 'action': 'help', 'parameters': {}}
        
        return {'service': 'unknown', 'action': 'help', 'parameters': {}}
    
    def get_smart_response(self, user_input: str, context: str = "") -> str:
        """Generate conversational response using LLM"""
        
        # If no API key, use fallback
        if not self.api_key:
            return self._get_fallback_response(user_input)
        
        print(f"[Perplexity] 💬 Generating conversational response for: '{user_input}'")
        
        try:
            import requests
            
            system_prompt = """You are a friendly AWS assistant. Answer questions conversationally.

IMPORTANT: Keep responses SHORT (1-2 sentences max). Be concise and friendly.

If asked about AWS/cloud services: Give a brief 1-sentence explanation, then say "I can help you manage EC2 instances and S3 buckets!"

If greeted: Respond warmly in 1 sentence and ask what they'd like to do.

Examples:
- "what is aws" → "AWS is Amazon's cloud platform for computing, storage, and more. I can help you manage EC2 instances and S3 buckets!"
- "how are you" → "I'm doing great! What would you like to do with your AWS resources today?"
- "what is ec2" → "EC2 provides virtual servers in the cloud. Want me to list your instances or create a new one?"

Keep it SHORT and actionable!"""
            
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 80,  # Shorter responses
                },
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                print(f"[Perplexity] ✅ Generated response: {content[:100]}...")
                return content
        
        except Exception as e:
            print(f"[Perplexity] ❌ Error generating response: {e}")
        
        return self._get_fallback_response(user_input)
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Fallback responses when LLM unavailable"""
        text = user_input.lower()
        
        if any(word in text for word in ['hi', 'hello', 'hey', 'how are you']):
            return """👋 Hi there! I'm your AWS Multi-Agent Assistant!

I can help you manage your AWS resources. What do you want me to do interesting today?

Try commands like:
  • "list my instances"
  • "create an ec2 instance"
  • "show me my s3 buckets"

Or type "help" to see everything I can do! 🚀"""
        
        return """🤖 Here's what I can do for you!

📦 EC2 Commands:
  • create ec2 instance [type]
  • list instances
  • stop instance <id>
  • terminate instance <id>

🗄️ S3 Commands:
  • create s3 bucket <name>
  • list buckets
  • delete bucket <name>
  • list objects in <bucket>

💡 Just use natural language - I'll understand! What would you like to try?"""
