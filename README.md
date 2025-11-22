# MTCloud - MikroTik Fleet Management Platform

A **multi-tenant SaaS** platform for MSPs to manage and monitor MikroTik network equipment across multiple clients and sites. Features real-time monitoring, AI-powered analytics, and comprehensive device management.

## 🏗️ Architecture

### Multi-Tenant Hierarchy
```
Global Admin (Titanium Computing)
  └── Organizations/MSPs (Your MSP, Partner MSPs)
      └── Clients (D Fox Law, Christiansen Plumbing, etc.)
          └── Sites (Round Rock Office, North Austin Office)
              └── Devices (MikroTik Routers, Switches, APs)
```

### Tech Stack
- **Backend**: FastAPI (Python 3.12) + PostgreSQL 17 + pgvector
- **Frontend**: React 18 + TypeScript + Vite
- **Real-time**: WebSockets for live metrics
- **Background Jobs**: Celery + Redis
- **AI/ML**: OpenAI, Anthropic, xAI, Self-hosted LLM support
- **MikroTik Integration**: RouterOS API (port 8728)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url> mtcloud
cd mtcloud

# Copy environment template
cp .env.example .env

# Edit .env with your settings (database password, API keys, etc.)
nano .env
```

### 2. Start Services
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/v1/docs
- **API Root**: http://localhost:8000

## 📋 Environment Configuration

Key environment variables in `.env`:

```bash
# Database
POSTGRES_USER=mtcloud
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=mtcloud_db

# Security
SECRET_KEY=your-super-secret-key-min-32-characters

# AI Providers (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
XAI_API_KEY=xai-...
LOCAL_LLM_URL=http://localhost:11434/v1  # For Ollama or similar
```

## 🗄️ Database Schema

### Core Multi-Tenant Tables
1. **organizations** - MSP/top-level entities
2. **clients** - Customer companies under MSPs
3. **sites** - Physical locations per client
4. **users** - Platform users with role-based access
5. **devices** - MikroTik network equipment
6. **device_metrics** - Time-series metrics
7. **interfaces** - Network interfaces
8. **interface_stats** - Interface statistics
9. **ai_insights** - AI-generated reports with vector embeddings
10. **ai_queries** - User AI query history

## 🔐 Access Control

| Role | Access |
|------|--------|
| **Global Admin** | Full platform access, manage all MSPs |
| **MSP Admin** | Manage their clients, sites, devices |
| **Client Admin** | View/manage their own sites and devices |
| **Technician** | Limited access for specific client sites |
| **Viewer** | Read-only dashboard access |

## 🤖 AI Features

### Natural Language Queries
```
"Show me all devices with high CPU at D Fox Law sites"
"Which sites had the most bandwidth usage last week?"
"List all offline routers in Round Rock"
```

### Scheduled AI Analysis
- Daily/weekly automated reports
- Anomaly detection
- Predictive alerts
- Optimization recommendations

### Multi-LLM Support
- **OpenAI** (GPT-4, GPT-4o)
- **Anthropic** (Claude 3.5 Sonnet)
- **xAI** (Grok)
- **Self-hosted** (Ollama, etc.)

## 🔧 Development

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run development server
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Database Migrations
```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📡 MikroTik Integration

### Supported Devices
- MikroTik Routers (RouterBOARD, CCR, hEX series)
- MikroTik Switches (CRS series)
- MikroTik Access Points (cAP, wAP series)

### API Endpoints Called
- `/system/resource/print` - System info, CPU, memory
- `/interface/print` - Interface list
- `/interface/monitor-traffic` - Real-time bandwidth
- `/ip/dhcp-server/lease/print` - DHCP leases
- `/interface/wireless/registration-table/print` - Wireless clients

### Device Requirements
- RouterOS v6.43+ (v7.x recommended)
- API enabled on port 8728
- User account with API + read permissions

## 🚢 Deployment

### Coolify Deployment (Recommended for On-Prem)
```bash
# Push to your Git repository
git push origin main

# In Coolify:
# 1. Create new resource → Docker Compose
# 2. Point to your repository
# 3. Set environment variables
# 4. Deploy
```

### Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Manual Docker Deployment
```bash
# Build images
docker compose build

# Run in production mode
docker compose --profile production up -d
```

## 📊 Monitoring & Logs

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f postgres

# Check service health
docker compose ps
```

## 🧪 Testing

```bash
cd backend
pytest

# With coverage
pytest --cov=app tests/
```

## 📈 Performance

- **Polling Interval**: 60 seconds (configurable)
- **WebSocket Updates**: 2-5 seconds for real-time metrics
- **Max Devices per Org**: 100 (configurable)
- **Database Connection Pool**: 10-20 connections

## 🔒 Security

- JWT-based authentication
- Encrypted device credentials (Fernet)
- HTTPS/WSS encryption
- Rate limiting on API endpoints
- SQL injection protection (SQLAlchemy ORM)
- Input validation (Pydantic)

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check database connection
docker compose logs postgres

# Check environment variables
docker compose config

# Restart services
docker compose restart backend
```

### Frontend build fails
```bash
# Clear node_modules
rm -rf frontend/node_modules
docker compose build --no-cache frontend
```

### MikroTik device won't connect
1. Verify API is enabled: `/ip service print`
2. Check firewall rules allow port 8728
3. Verify credentials
4. Test connectivity: `telnet <device-ip> 8728`

## 📝 Project Structure

```
mtcloud/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── tasks/        # Celery tasks
│   ├── alembic/          # Database migrations
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── store/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🗺️ Roadmap

- [x] Multi-tenant architecture design
- [x] Docker Compose setup
- [x] PostgreSQL + pgvector integration
- [ ] Database models and migrations
- [ ] Authentication & RBAC
- [ ] Device management CRUD
- [ ] Real-time monitoring (WebSockets)
- [ ] MikroTik API integration
- [ ] AI-powered analytics
- [ ] Frontend dashboard
- [ ] Mobile-responsive UI
- [ ] Email alerts
- [ ] Configuration backup/restore

## 📄 License

Proprietary - Titanium Computing

## 👥 Team

- **Platform Owner**: Titanium Computing
- **Development**: [Your Team]

## 🆘 Support

For support, email: support@titaniumcomputing.com

---

**Built with ❤️ for MSPs managing MikroTik networks**
