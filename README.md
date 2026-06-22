# 🏢 Autonomous Supply Chain Management System

An intelligent supply chain management system powered by AI that helps you interact with your Odoo ERP backend through natural language. This application uses advanced language models and the Model Context Protocol (MCP) to understand your supply chain queries and execute operations autonomously, making ERP interactions seamless and intuitive.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Clone the Repository](#clone-the-repository)
- [Setup on Local System](#setup-on-local-system)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Natural Language Queries**: Ask questions about your supply chain in plain English
- **AI-Powered Agent**: Leverages LangChain, LangGraph, and Groq for intelligent operations
- **Odoo ERP Integration**: Seamless integration with Odoo 17.0 for comprehensive supply chain management
- **Model Context Protocol (MCP)**: Standardized protocol for tool communication and extensibility
- **Inventory Management**: Check warehouse stock levels and product availability in real-time
- **Order Monitoring**: Track delayed orders and fulfillment bottlenecks
- **Interactive UI**: User-friendly Streamlit interface for operators and managers
- **Real-time Analysis**: Live ERP system analysis and reporting
- **Docker Containerized**: Easy deployment with pre-configured Docker Compose setup
- **Secure API Key Management**: Safe handling of credentials through UI input fields

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client (Streamlit)                    │
│              Supply Chain Command Center UI                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Server (FastAPI)                             │
│      Autonomous Supply Chain Tools & Operations              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ RPC
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Odoo 17.0 ERP Backend                       │
│     Supply Chain, Inventory, Orders Management               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │
                           ▼
                  ┌──────────────────┐
                  │   PostgreSQL DB  │
                  └──────────────────┘
```

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** - [Download Docker](https://www.docker.com/products/docker-desktop) (Recommended for easy setup)
- **Docker Compose** - Usually comes with Docker Desktop
- **Python 3.10+** - [Download Python](https://www.python.org/downloads/) (For local development without Docker)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Groq API Key** - [Get Free Groq API Key](https://console.groq.com) (For AI inference)

## 🔧 Clone the Repository

```bash
git clone https://github.com/VireshShah17/Autonomous-Supply-Chain.git
cd autonomous-supply-chain
```

## 🚀 Setup on Local System

### Option 1: Using Docker Compose (Recommended)

#### 1. Build and Start All Services

```bash
docker-compose up -d
```

This will:

- Start PostgreSQL database
- Initialize Odoo 17.0 backend
- Start the MCP Server (FastAPI)
- Start the MCP Client (Streamlit)

#### 2. Wait for Services to Initialize

The first startup may take 2-3 minutes as Odoo initializes. You can check the logs:

```bash
docker-compose logs -f
```

#### 3. Access the Services

- **Odoo ERP**: http://localhost:8069
- **MCP Client (Supply Chain Agent)**: http://localhost:8501
- **MCP Server API**: http://localhost:8000

---

### Option 2: Local Development Setup (Without Docker)

#### 1. Create Virtual Environments

**For MCP Server:**

```bash
cd mcp-server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**For MCP Client (in a separate terminal):**

```bash
cd mcp-client
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies

**For MCP Server:**

```bash
cd mcp-server
pip install -r requirements.txt
```

**For MCP Client:**

```bash
cd mcp-client
pip install -r requirements.txt
```

#### 3. Set Up Odoo Backend (Docker Only - Recommended)

If you want to run only the Odoo backend via Docker:

```bash
docker run -d -p 8069:8069 \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo_password \
  odoo:17.0
```

Or use a simplified docker-compose with just the database and Odoo:

```bash
docker-compose up db web -d
```

## 🔐 Environment Variables

### For MCP Server

Create a `.env` file in the `mcp-server/` directory:

```bash
touch mcp-server/.env
```

Add the following:

```
# Odoo Connection (when running Odoo via Docker)
ODOO_URL=http://localhost:8069
```

### For MCP Client

Create a `.env` file in the `mcp-client/` directory:

```bash
touch mcp-client/.env
```

Add the following:

```
# MCP Server Connection
MCP_SERVER_URL=http://localhost:8000

# Streamlit Configuration (optional)
STREAMLIT_SERVER_HEADLESS=true
```

### Groq API Key

The Groq API key is entered directly in the Streamlit sidebar when running the application (for security reasons, it's not stored in `.env`).

**Important**: Never commit `.env` files to version control. They're already listed in `.gitignore`.

## ▶️ Running the Application

### Using Docker Compose (Recommended)

#### Start All Services

```bash
docker-compose up -d
```

#### View Logs

```bash
docker-compose logs -f mcp-client
```

#### Stop All Services

```bash
docker-compose down
```

#### Stop and Remove All Data

```bash
docker-compose down -v
```

---

### Local Development

#### Terminal 1: Start MCP Server

```bash
cd mcp-server
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server will be available at: http://localhost:8000

#### Terminal 2: Start MCP Client

```bash
cd mcp-client
source venv/bin/activate
streamlit run app/main.py
```

Client will be available at: http://localhost:8501

---

## 📋 Using the Application

### 1. Access the Supply Chain Command Center

Open your browser and navigate to:

```
http://localhost:8501
```

### 2. Enter Groq API Key

- In the left sidebar under "Configuration"
- Enter your Groq API Key (get a free key from [console.groq.com](https://console.groq.com))
- The system will validate and initialize the AI agent

### 3. Ask Supply Chain Queries

Enter natural language queries such as:

**Inventory Queries:**

- "What's the current stock level for desks?"
- "Show me all products with low inventory"
- "How much warehouse space is available?"

**Order Management:**

- "Which orders are delayed?"
- "Show me orders that need urgent attention"
- "What's the status of order #12345?"

**Routing & Logistics:**

- "Optimize the delivery route for tomorrow"
- "What shipments are pending?"

### 4. View Real-time Results

The AI agent will:

1. Parse your natural language query
2. Call appropriate supply chain tools via MCP
3. Fetch data from Odoo ERP
4. Analyze and format results
5. Display actionable insights

---

## 📁 Project Structure

```
autonomous-supply-chain/
├── docker-compose.yml          # Docker orchestration
├── README.md                   # This file
│
├── mcp-client/                 # Streamlit UI & Agent
│   ├── Dockerfile              # Client container setup
│   ├── requirements.txt         # Python dependencies
│   └── app/
│       ├── main.py             # Streamlit app entry point
│       ├── agent.py            # LangChain agent initialization
│       └── custom_logging.py   # Logging configuration
│
├── mcp-server/                 # FastAPI MCP Server
│   ├── Dockerfile              # Server container setup
│   ├── requirements.txt         # Python dependencies
│   └── app/
│       ├── main.py             # FastAPI server entry point
│       ├── tools.py            # Supply chain tool definitions
│       ├── odoo_client.py       # Odoo API client
│       └── custom_logging.py   # Logging configuration
│
└── odoo-backend/               # Odoo ERP customizations
    ├── addons/                 # Custom Odoo modules
    └── config/                 # Odoo configuration files
```

---

## 🔌 API Documentation

### MCP Server Endpoints

#### Get Available Tools

```bash
curl http://localhost:8000/tools
```

**Response:**

```json
{
  "tools": [
    {
      "name": "check_inventory",
      "description": "Checks warehouse stock levels and quantities for a specific product",
      "input_schema": { ... }
    },
    {
      "name": "get_delayed_orders",
      "description": "Retrieves open sales orders facing delivery fulfillment bottlenecks",
      "input_schema": { ... }
    }
    // ... more tools
  ]
}
```

#### Call a Tool

```bash
curl -X POST http://localhost:8000/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "check_inventory",
    "arguments": {
      "product_name_query": "Desk"
    }
  }'
```

---

## 🛠️ Troubleshooting

### Issue: "Could not connect to Odoo"

**Solution:**

- Ensure Odoo is running: `docker-compose logs web`
- Wait 2-3 minutes for Odoo to initialize
- Check if ports are available: `lsof -i :8069`

### Issue: Streamlit app not loading

**Solution:**

- Check client logs: `docker-compose logs mcp-client`
- Verify MCP Server is running: `docker-compose logs mcp-server`
- Restart services: `docker-compose restart`

### Issue: "Invalid Groq API Key"

**Solution:**

- Generate a new key at [console.groq.com](https://console.groq.com)
- Ensure key is copied completely without spaces
- Try again in the sidebar

### Issue: Port already in use

**Solution:**

- Identify process using port: `lsof -i :PORT_NUMBER`
- Kill process: `kill -9 PID`
- Or change ports in `docker-compose.yml`

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Report Issues

Found a bug? [Open an issue](https://github.com/VireshShah17/Autonomous-Supply-Chain/issues) with:

- Clear description of the problem
- Steps to reproduce
- Screenshots if applicable
- Your environment details

### Submit Code Changes

1. **Fork** the repository
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and test thoroughly
4. **Commit with clear messages**:
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/tests if applicable

### Development Guidelines

- Follow PEP 8 style for Python code
- Add docstrings to new functions
- Write unit tests for new features
- Update documentation as needed
- Test with Docker before submitting PR

---

## 📚 Technology Stack

- **Backend ERP**: Odoo 17.0
- **Database**: PostgreSQL 15
- **MCP Server**: FastAPI with Uvicorn
- **MCP Client**: Streamlit
- **AI/ML**: LangChain, LangGraph, Groq LLM
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.10+

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

- 📧 Email: vireshshah17062004@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/VireshShah17/Autonomous-Supply-Chain/issues)

---

## 🎉 Getting Started Quick Reference

```bash
# Clone and navigate
git clone https://github.com/VireshShah17/Autonomous-Supply-Chain.git
cd autonomous-supply-chain

# Start with Docker (easiest)
docker-compose up -d

# Wait 2-3 minutes for services to initialize
sleep 180

# Access the application
# Odoo: http://localhost:8069
# Supply Chain Agent: http://localhost:8501
# API: http://localhost:8000

# View logs
docker-compose logs -f mcp-client

# Stop services
docker-compose down
```

---

**Ready to revolutionize your supply chain? Let's get started! 🚀**
