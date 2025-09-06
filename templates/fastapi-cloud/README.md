# FastAPI Cloud Template
# Production-ready FastAPI application with security, scalability, and cloud-native features

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional)
- MongoDB (optional)
- Redis (optional)

### 1. Setup Environment

```bash
# Clone and navigate
cd templates/fastapi-cloud

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements-dev.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Minimum required: SECRET_KEY, JWT_SECRET_KEY
```

### 3. Run Application

```bash
# Development mode
python main.py

# Production mode
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 4. Access Application

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: Prevent API abuse
- **Security Headers**: OWASP recommended headers
- **Password Hashing**: bcrypt with salt
- **Input Validation**: Pydantic models
- **CORS Protection**: Configurable origins
- **SQL Injection Prevention**: SQLAlchemy ORM

## 📊 Database Support

- **PostgreSQL**: Primary async database
- **MongoDB**: Document storage
- **Redis**: Caching and sessions
- **Connection Pooling**: Optimized performance
- **Health Checks**: Monitor connections

## ☁️ Cloud Ready

- **Docker**: Multi-stage production builds
- **Kubernetes**: Production manifests
- **Multi-cloud**: AWS, GCP, Azure support
- **Monitoring**: Prometheus metrics
- **Logging**: Structured JSON logs
- **Health Checks**: Kubernetes probes

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Current user info

### Users
- `GET /users/` - List users (admin)
- `GET /users/{id}` - Get user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Health
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed system status
- `GET /health/ready` - Kubernetes readiness
- `GET /health/live` - Kubernetes liveness

### Monitoring
- `GET /metrics` - Prometheus metrics

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Load testing
pip install locust
locust -f tests/load_test.py
```

## 📦 Docker Deployment

```bash
# Build image
docker build -t fastapi-cloud .

# Run container
docker run -p 8000:8000 -e ENVIRONMENT=production fastapi-cloud

# Docker Compose
docker-compose up -d
```

## ☸️ Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=fastapi-cloud
```

## 🔧 Configuration

Key environment variables:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
PORT=8000
WORKERS=4

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_EXPIRE_MINUTES=1440

# Database
POSTGRES_HOST=localhost
POSTGRES_USER=fastapi
POSTGRES_PASSWORD=password
POSTGRES_DB=fastapi_db

# Features
ENABLE_REGISTRATION=true
ENABLE_RATE_LIMITING=true
ENABLE_API_DOCS=false  # Disable in production
```

## 📈 Performance

- **Async/Await**: Non-blocking I/O
- **Connection Pooling**: Database optimization
- **Caching**: Redis integration
- **Rate Limiting**: Prevent abuse
- **Compression**: Gzip middleware
- **Static Files**: Efficient serving

## 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Pre-commit hooks
pre-commit install
```

## 📋 Project Structure

```
fastapi-cloud/
├── app/
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connections
│   ├── middleware/         # Security, auth, logging
│   ├── models/            # Pydantic & SQLAlchemy models
│   ├── routers/           # API route handlers
│   ├── services/          # Business logic
│   └── utils/             # Utilities and helpers
├── tests/                 # Test cases
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Local development
└── README.md             # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create GitHub issue
- Check documentation
- Review example code

---

**Built for Hackathons** 🏆  
Ready for Production 🚀  
Secure by Default 🛡️
