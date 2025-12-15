# A2AForge - Crafting Intelligent Cloud Agents with A2A and MCP

**Team Name:** Cloud Busters  
**Team Members:** Chandini Saisri Uppuganti, Apurva Karne, Roshini Joga, Harshavardhan Reddy 

Links:

Youtube: [Project Demo & PPT Presentation](https://youtu.be/H-yxuoetoqk)

Report: [Project Report](https://docs.google.com/document/d/1XLSRa4whxHoxZoe-oDYYpWNul1L9hwTujFq7g09t5TY/edit?tab=t.0)

PPT: [Presentation Slides](https://sjsu0-my.sharepoint.com/:p:/g/personal/chandinisaisri_uppuganti_sjsu_edu/IQDKHQMG5-BXT6Mv5cjo0Ju5AWJXYdkGAFNU9UFufsekCpU?e=N6fiGo)

## Overview

A2AForge is an AI-driven multi-agent system designed to simplify and automate cloud infrastructure management using natural language commands. It brings together the Agent-to-Agent (A2A) protocol by Google, the Model Context Protocol (MCP) by Anthropic, and the OpenAI Agents SDK to enable seamless communication and task execution between autonomous agents.

At its core, this project showcases how intelligent agents can collaboratively interpret user instructions, communicate internally, and take real-world actions in the cloud — such as provisioning or terminating AWS EC2 instances, creating and managing S3 buckets, and eventually more (like Lambda, RDS, and CloudWatch integration).

By combining protocol-based agent communication with AI capabilities, Cloud Busters demonstrates the future of cloud DevOps: where human operators only need to say "Create an EC2 instance" and the system handles the rest.

This project is built under the internal codename **A2AForge**, reflecting its purpose — a "forge" for building and orchestrating multi-agent cloud tools via A2A.

Whether you're a DevOps engineer, AI researcher, or just cloud-curious, A2AForge offers an exciting proof-of-concept of how modern AI can automate complex infrastructure tasks.

## What Makes It Special?

- **Autonomous Collaboration**: Agents communicate and delegate tasks using A2A — no centralized controller needed.
- **Tool-Augmented Reasoning**: Powered by MCP, agents can decide when and how to use specific cloud tools.
- **Natural Language UX**: Users interact with the system using plain English, lowering the barrier for non-engineers.
- **Modular Agent Design**: Each cloud service (EC2, S3, etc.) has its own specialized agent, making the system scalable and extensible.
- **Production-Ready Concepts**: While a proof-of-concept, the architecture mirrors real-world production readiness using OpenAI's SDK, AWS best practices, and environment-secure deployment.

## Architecture

- **Coordinator Agent**: Routes requests and orchestrates A2A communication
- **EC2 Agent**: Handles EC2 instance operations
- **S3 Agent**: Handles S3 bucket operations
- **A2A Communication**: Agents can query and collaborate with each other
- **Perplexity AI**: Enhanced natural language understanding
- **MCP Integration**: Uses Model Context Protocol for AWS operations

### A2A Communication Flow
```
User Request
    ↓
Coordinator Agent
    ↓ ↔ ↓
EC2 Agent ⟷ S3 Agent
    ↓
AWS Services
```

Agents can:
- Send messages to each other
- Query other agents for information
- Share context and collaborate
- Maintain conversation history

## Features

### Multi-Agent Intelligence
Modular agent architecture — EC2 Agent, S3 Agent, and more coming soon.

### Protocol-Driven Communication
Integrates Google's A2A with Anthropic's MCP for seamless agent collaboration.

### Cloud Resource Management
Automates AWS EC2 instance provisioning/termination and S3 bucket operations.

### Natural Language Interface
Command AWS resources via plain English prompts.

## Agent Capabilities

| Agent | Tool Functions |
|-------|----------------|
| EC2 Agent | `initiate_aws_ec2_instance`, `terminate_aws_ec2_instance` |
| S3 Agent | `create_s3_bucket`, `delete_s3_bucket`, `list_s3_buckets` |
| (Coming Soon) | Lambda Agent, IAM Agent, Cost Monitor Agent, CloudWatch Agent |

## Prerequisites

- Python 3.12+ or Docker
- AWS IAM Role with EC2/S3 permissions

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```bash
# AWS Credentials (or use aws configure)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Perplexity API Key (optional - for enhanced NLP)
PERPLEXITY_API_KEY=your_perplexity_api_key
```

**Get Perplexity API Key:**
1. Visit https://www.perplexity.ai/settings/api
2. Sign up and get your API key
3. Add it to `.env` file

**Or use AWS CLI:**
```bash
aws configure
```

### 3. Install MCP Server (Optional)

If you want to use MCP tools:

```bash
# Install uv/uvx if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The MCP server will auto-start when Kiro loads the configuration.

## Usage

### Start the Chat Interface

```bash
python chat_interface.py
```

### Example Commands

**EC2 Operations:**
- `create ec2 instance` - Create a t2.micro instance
- `create ec2 instance t2.small` - Create specific instance type
- `list instances` - Show all EC2 instances
- `stop instance i-1234567890abcdef0` - Stop an instance
- `terminate instance i-1234567890abcdef0` - Terminate an instance

**S3 Operations:**
- `create s3 bucket my-unique-bucket-name` - Create a bucket
- `create s3 bucket my-bucket in us-west-2` - Create in specific region
- `list buckets` - Show all S3 buckets
- `list objects in my-bucket` - List objects in a bucket
- `delete bucket my-bucket` - Delete a bucket

## Project Structure

```
.
├── .kiro/settings/mcp.json    # MCP configuration
├── agents/
│   ├── coordinator.py          # Main router agent
│   ├── ec2_agent.py           # EC2 specialist
│   └── s3_agent.py            # S3 specialist
├── chat_interface.py          # CLI interface
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Current Features

- ✅ **LLM-Powered Intent Recognition** - Perplexity AI handles ALL command parsing
- ✅ Natural language understanding (polite requests, location names, etc.)
- ✅ Specialized agents for EC2 and S3
- ✅ Agent-to-agent communication (A2A)
- ✅ Smart region mapping (Virginia → us-east-1, Tokyo → ap-northeast-1)
- ✅ MCP integration ready
- ✅ Beautiful web UI with animations
- ✅ CLI interface

## Roadmap

1. **Enhanced Web Interface**: Expand React/Next.js frontend capabilities
2. **Additional Cloud Services**: Lambda, RDS, CloudFormation, IAM, CloudWatch
3. **Authentication & Security**: Secure the interface with proper auth
4. **Comprehensive Logging**: Track all operations and agent interactions
5. **Rollback Capabilities**: Undo operations if needed
6. **Cost Monitoring**: Real-time AWS cost tracking and alerts

## Security Notes

- Never commit AWS credentials to version control
- Use IAM roles with minimal required permissions
- Enable MFA on your AWS account
- Review all operations before execution in production
