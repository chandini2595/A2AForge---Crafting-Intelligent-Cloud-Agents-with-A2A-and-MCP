"""
Base Agent class with A2A (Agent-to-Agent) communication capabilities
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class Message:
    """Message structure for A2A communication"""
    
    def __init__(self, sender: str, receiver: str, content: Any, msg_type: str = "request"):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.msg_type = msg_type  # request, response, notification, query
        self.timestamp = datetime.now().isoformat()
        self.id = f"{sender}-{receiver}-{datetime.now().timestamp()}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.msg_type,
            "timestamp": self.timestamp
        }


class BaseAgent:
    """Base class for all agents with A2A communication"""
    
    def __init__(self, name: str):
        self.name = name
        self.message_queue: List[Message] = []
        self.agents_registry: Dict[str, 'BaseAgent'] = {}
        self.conversation_history: List[Dict[str, Any]] = []
    
    def register_agent(self, agent: 'BaseAgent'):
        """Register another agent for A2A communication"""
        self.agents_registry[agent.name] = agent
        print(f"[A2A] {self.name} registered {agent.name}")
    
    def send_message(self, receiver: str, content: Any, msg_type: str = "request") -> Optional[Any]:
        """Send a message to another agent"""
        if receiver not in self.agents_registry:
            print(f"[A2A] Error: {receiver} not found in registry")
            return None
        
        message = Message(self.name, receiver, content, msg_type)
        self.conversation_history.append(message.to_dict())
        
        print(f"[A2A] {self.name} → {receiver}: {msg_type}")
        
        # Deliver message to receiver
        target_agent = self.agents_registry[receiver]
        return target_agent.receive_message(message)
    
    def receive_message(self, message: Message) -> Any:
        """Receive and process a message from another agent"""
        self.message_queue.append(message)
        self.conversation_history.append(message.to_dict())
        
        print(f"[A2A] {self.name} ← {message.sender}: {message.msg_type}")
        
        # Process the message
        return self.handle_message(message)
    
    def handle_message(self, message: Message) -> Any:
        """Override this method to handle incoming messages"""
        return {"status": "received", "message": "Message received but not processed"}
    
    def broadcast(self, content: Any, msg_type: str = "notification"):
        """Broadcast a message to all registered agents"""
        responses = {}
        for agent_name in self.agents_registry:
            response = self.send_message(agent_name, content, msg_type)
            responses[agent_name] = response
        return responses
    
    def query_agent(self, agent_name: str, query: str) -> Any:
        """Query another agent for information"""
        return self.send_message(agent_name, {"query": query}, "query")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.conversation_history
