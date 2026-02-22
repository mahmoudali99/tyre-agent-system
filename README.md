# Matrax Tyres Multi-Agent System

A production-ready tyre company management system with AI-powered multi-agent chat, built with **FastAPI**, **Langchain**, **PostgreSQL**, **Qdrant**, **Next.js**, and **Docker**.

## 🚀 Quick Start

```bash
# Run the project
docker compose up --build
```

**Access URLs:**
- **Frontend**: http://localhost:3007
- **Backend API**: http://localhost:4007/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## 📋 Project Overview

Matrax Tyres is an intelligent tyre management system that uses **5 specialized AI agents** working together to provide seamless customer service, inventory management, and order processing. The system leverages **RAG (Retrieval-Augmented Generation)** with vector search to deliver accurate, context-aware responses.

### Key Features

- **Multi-Agent AI Chat** — 5 specialized agents powered by Google Gemini
- **RAG (Retrieval-Augmented Generation)** — Qdrant vector search over car brands, car models, tyre brands, and tyres
- **Full CRUD** — Manage car brands, car models, tyre brands, tyres, orders, and stock
- **Auto-sync Qdrant** — Creating or updating records automatically updates Qdrant embeddings
- **Real-time Dashboard** — Live statistics and analytics
- **Order Management** — Complete order lifecycle with status tracking (MTX-XXXXX format)
- **Stock Management** — Real-time inventory tracking and low-stock alerts
- **Docker Compose** — One command to run everything

## 🏗️ Architecture

```
User → Next.js Frontend (Port 3007) → FastAPI Backend (Port 4007) → PostgreSQL (data)
                                                                    → Qdrant (vector search)
                                                                    → Gemini (LLM + embeddings)
```

## 🤖 AI Agents

The system consists of **5 specialized AI agents**, each with a specific responsibility:

### 1. **Agent Orchestrator**
**Responsibility:** Central coordinator that routes user requests to the appropriate specialized agent
- Classifies user intent using Gemini LLM
- Routes to: `recommendation`, `inventory`, `order_placement`, `order_status`, or `general`
- Manages conversation flow and agent handoffs
- Maintains chat history and context

### 2. **Recommendation Agent**
**Responsibility:** Provides intelligent tyre recommendations based on car information
- Searches Qdrant vector database for matching car models
- Retrieves compatible tyre sizes for the user's vehicle
- Finds available tyres matching those sizes
- Generates natural language recommendations with pricing
- Filters out-of-stock items automatically

### 3. **Inventory Agent**
**Responsibility:** Real-time stock checking and inventory queries
- Checks stock levels by tyre ID or size
- Identifies low-stock items (below minimum threshold)
- Provides availability information
- Supports bulk stock queries

### 4. **Order Agent**
**Responsibility:** Order creation, validation, and retrieval
- Creates orders with automatic stock deduction
- Validates stock availability before order placement
- Calculates order totals and generates order codes (MTX-XXXXX format)
- Retrieves order details by ID or order code
- Manages order status updates

### 5. **Customer Agent** (Legacy/Fallback)
**Responsibility:** General customer inquiries and fallback handler
- Handles general questions about the business
- Provides information about services
- Fallback for unclassified intents

### RAG Collections (Qdrant)

| Collection | Embedded Text | Payload |
|------------|--------------|---------|
| `car_brands` | Brand name | Full record (id, name, country) |
| `car_models` | "Brand Model Year" | Full record (id, brand_id, brand_name, name, year, tyre_sizes) |
| `tyre_brands` | Brand name | Full record (id, name, country) |
| `tyres` | "Brand Model Size" | Full record (id, brand_id, brand_name, model, size, type, price, stock) |

## 🛠️ Setup Instructions

### Prerequisites

- Docker & Docker Compose
- A [Google Gemini API key](https://aistudio.google.com/apikey)
- Git

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/tyre-agent-system.git
   cd tyre-agent-system
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file and configure for local development:**
   ```bash
   # Gemini API Key
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Environment: development or production
   NODE_ENV=development
   
   # API URL Configuration
   NEXT_PUBLIC_API_URL=http://localhost:4007/api
   ```

4. **Run the project:**
   ```bash
   docker compose up --build
   ```

5. **Access the application:**
   - **Frontend**: http://localhost:3007
   - **Backend API**: http://localhost:4007/docs
   - **Qdrant Dashboard**: http://localhost:6333/dashboard

The backend automatically seeds the database and Qdrant on first startup.

### Production Server Deployment (185.137.122.199)

1. **SSH into your server:**
   ```bash
   ssh user@185.137.122.199
   ```

2. **Clone or pull the repository:**
   ```bash
   # First time
   git clone https://github.com/your-username/tyre-agent-system.git
   cd tyre-agent-system
   
   # Or update existing
   cd tyre-agent-system
   git pull origin main
   ```

3. **Configure `.env` for production:**
   ```bash
   nano .env
   ```
   
   Set the following:
   ```bash
   # Gemini API Key
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Environment: production
   NODE_ENV=production
   
   # API URL Configuration (use server IP)
   NEXT_PUBLIC_API_URL=http://185.137.122.199:4007/api
   ```

4. **Stop existing containers (if any):**
   ```bash
   docker compose down
   ```

5. **Build and run:**
   ```bash
   docker compose up --build -d
   ```

6. **Check logs:**
   ```bash
   docker compose logs -f
   ```

7. **Access the application:**
   - **Frontend**: http://185.137.122.199:3007
   - **Backend API**: http://185.137.122.199:4007/docs
   - **Qdrant Dashboard**: http://185.137.122.199:6333/dashboard

### Updating on Server

```bash
# SSH into server
ssh user@185.137.122.199

# Navigate to project
cd tyre-agent-system

# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose up --build -d

# Check status
docker compose ps
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/stats` | Dashboard statistics |
| `GET/POST/PUT/DELETE` | `/api/car-brands` | Car brands CRUD |
| `GET/POST/PUT/DELETE` | `/api/car-models` | Car models CRUD |
| `GET/POST/PUT/DELETE` | `/api/tyre-brands` | Tyre brands CRUD |
| `GET/POST/PUT/DELETE` | `/api/tyres` | Tyres CRUD |
| `GET` | `/api/tyres/stock` | Get stock information |
| `PUT` | `/api/tyres/{id}/stock` | Update stock for specific tyre |
| `GET` | `/api/orders` | Get all orders |
| `GET` | `/api/orders/{id}` | Get order by ID |
| `POST` | `/api/orders` | Create new order |
| `PUT` | `/api/orders/{id}/status` | Update order status |
| `DELETE` | `/api/orders/{id}` | Delete order |
| `POST` | `/api/chat` | AI chat (multi-agent) |
| `GET` | `/api/chat/sessions` | Get chat sessions |
| `GET` | `/api/chat/sessions/{id}/messages` | Get messages for session |
| `POST` | `/api/seed` | Seed database + Qdrant |
| `GET` | `/api/health` | Health check |

## 💬 Chat Flow Example

### Scenario 1: Tyre Recommendation
```
User: "I need tyres for Mercedes C-Class 2024"
  ↓
1. Orchestrator classifies intent as "recommendation"
2. Recommendation Agent searches Qdrant for "Mercedes C-Class 2024"
3. Finds matching car model with compatible tyre sizes
4. Searches tyres collection for matching sizes with stock > 0
5. Returns recommendations with brand, model, size, price, and stock
6. User selects a tyre and quantity
7. Orchestrator routes to Order Agent
8. Order Agent creates order, deducts stock, generates order code (MTX-00001)
9. Returns order confirmation with total and order code
```

### Scenario 2: Order Status Check
```
User: "What's the status of MTX-00002?"
  ↓
1. Orchestrator classifies intent as "order_status"
2. Order Agent retrieves order by code MTX-00002
3. Returns order details: status, customer, items, total
4. Provides next steps based on current status
```

### Scenario 3: Stock Check
```
User: "Do you have Michelin Pilot Sport 4 in stock?"
  ↓
1. Orchestrator classifies intent as "inventory"
2. Inventory Agent searches for matching tyres
3. Returns stock levels and availability
```

## Project Structure

```
tyre-agent-system/
├── backend/
│   ├── agents/          # Customer, Recommendation, Inventory, Order agents
│   ├── api/             # FastAPI route handlers
│   ├── models/          # SQLAlchemy models + Pydantic schemas
│   ├── rag/             # Qdrant client + Gemini embeddings
│   ├── config.py        # Settings
│   ├── database.py      # DB connection
│   ├── main.py          # FastAPI app
│   ├── seed.py          # Database + Qdrant seeder
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   ├── lib/api.ts       # API client
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Langchain, Google Gemini
- **Frontend**: Next.js 16, React 19, TailwindCSS, shadcn/ui, Lucide Icons
- **Database**: PostgreSQL 16
- **Vector DB**: Qdrant
- **Embeddings**: Gemini `models/gemini-embedding-001` (768 dimensions)
- **LLM**: Gemini 2.5 Flash
- **Containerization**: Docker Compose

## 🌐 Ports Configuration

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3007 | http://localhost:3007 |
| Backend API | 4007 | http://localhost:4007 |
| PostgreSQL | 5432 | localhost:5432 |
| Qdrant | 6333 | http://localhost:6333 |
| Qdrant gRPC | 6334 | localhost:6334 |

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `NODE_ENV` | Environment mode | `development` or `production` |
| `NEXT_PUBLIC_API_URL` | Frontend API endpoint | `http://localhost:4007/api` (dev)<br>`http://185.137.122.199:4007/api` (prod) |

## 🎯 Features Breakdown

### Order Management
- Order code format: `MTX-XXXXX` (e.g., MTX-00001)
- Status tracking: Pending → Confirmed → Processing → Ready → Shipped → Delivered → Completed
- Admin can update order status from UI
- Search orders by code, customer name, or ID
- Automatic stock deduction on order placement

### Stock Management
- Real-time inventory tracking
- Low-stock alerts (items below minimum threshold)
- Critical stock warnings
- Stock update from admin panel
- Automatic sync between `/tyres` and `/stock` pages

### Chat Interface
- Multi-turn conversations with context
- Session management
- Intent classification
- Natural language understanding
- Order status lookup via chat

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :3007
lsof -i :4007

# Kill the process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Reset database
docker compose down -v
docker compose up --build
```

### Qdrant Not Syncing
```bash
# Re-seed data
curl -X POST http://localhost:4007/api/seed
```

## 📄 License

MIT License
