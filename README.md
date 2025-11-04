# A2AForge - Crafting Intelligent Cloud Agents with A2A and MCP

## Team Name: Cloud Busters 
## Team Members:
*Chandini Saisri Uppuganti*

*Apurva Karne*

*Roshini Joga*


## Overview

**A2AForge** is an AI-driven multi-agent system designed to simplify and automate cloud infrastructure management using natural language commands. It brings together the **Agent-to-Agent (A2A)** protocol by Google, the **Model Context Protocol (MCP)** by Anthropic, and the **OpenAI Agents SDK** to enable seamless communication and task execution between autonomous agents.

At its core, this project showcases how intelligent agents can collaboratively interpret user instructions, communicate internally, and take real-world actions in the cloud — such as provisioning or terminating AWS EC2 instances, creating and managing S3 buckets, and eventually more (like Lambda, RDS, and CloudWatch integration).

By combining protocol-based agent communication with AI capabilities, **Cloud Busters** demonstrates the future of cloud DevOps: where human operators only need to say *"Create an EC2 instance"* and the system handles the rest.

This project is built under the internal codename **A2AForge**, reflecting its purpose — a “forge” for building and orchestrating multi-agent cloud tools via A2A.

Whether you're a DevOps engineer, AI researcher, or just cloud-curious, **A2AForge** offers an exciting proof-of-concept of how modern AI can automate complex infrastructure tasks

### What Makes It Special?

- **Autonomous Collaboration:** Agents communicate and delegate tasks using A2A — no centralized controller needed.
- **Tool-Augmented Reasoning:** Powered by MCP, agents can decide when and how to use specific cloud tools.
- **Natural Language UX:** Users interact with the system using plain English, lowering the barrier for non-engineers.
- **Modular Agent Design:** Each cloud service (EC2, S3, etc.) has its own specialized agent, making the system scalable and extensible.
- **Production-Ready Concepts:** While a proof-of-concept, the architecture mirrors real-world production readiness using OpenAI’s SDK, AWS best practices, and environment-secure deployment.


## Features

-  **Multi-Agent Intelligence**  
  Modular agent architecture — EC2 Agent, S3 Agent, and more coming soon.

-  **Protocol-Driven Communication**  
  Integrates Google's A2A with Anthropic’s MCP for seamless agent collaboration.

-  **Cloud Resource Management**  
  Automates AWS EC2 instance provisioning/termination and S3 bucket operations.

-  **Natural Language Interface**  
  Command AWS resources via plain English prompts.

---

## Agent Capabilities

| Agent      | Tool Functions                                                 |
|------------|----------------------------------------------------------------|
| EC2 Agent  | `initiate_aws_ec2_instance`, `terminate_aws_ec2_instance`      |
| S3 Agent   | `create_s3_bucket`, `delete_s3_bucket`, `list_s3_buckets`      |
| (Coming Soon) | Lambda Agent, IAM Agent, Cost Monitor Agent, CloudWatch Agent |

---

## Prerequisites

- Python 3.12+ or Docker
- AWS IAM Role with EC2/S3 permissions
