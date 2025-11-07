# 🚀 Start Web UI

## Quick Start

### 1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Backend API

```bash
cd backend
python main.py
```

Backend will run on: http://localhost:8000

### 3. Install Frontend Dependencies (in a new terminal)

```bash
cd frontend
npm install
```

### 4. Start Frontend

```bash
npm run dev
```

Frontend will run on: http://localhost:3000

## Access the App

Open your browser to: **http://localhost:3000**

## Features

- 💬 Chat interface with natural language commands
- 🚀 Quick command buttons
- ✅ Success/error indicators
- 📊 JSON response formatting
- 🎨 Beautiful gradient UI
- 📱 Responsive design

## Example Commands

- `create ec2 instance`
- `create ec2 instance t2.small`
- `list instances`
- `stop instance i-xxxxx`
- `terminate instance i-xxxxx`
- `create s3 bucket my-bucket-name`
- `list buckets`
- `delete bucket my-bucket-name`

## Architecture

```
Frontend (React + Vite)
    ↓ HTTP
Backend (FastAPI)
    ↓
Coordinator Agent
    ↓
EC2 Agent / S3 Agent
    ↓
AWS (boto3)
```

## Troubleshooting

**CORS errors?**
- Make sure backend is running on port 8000
- Check CORS settings in backend/main.py

**Can't connect to AWS?**
- Verify AWS credentials: `aws configure`
- Check your AWS region

**Port already in use?**
- Backend: Change port in backend/main.py
- Frontend: Change port in frontend/vite.config.js
