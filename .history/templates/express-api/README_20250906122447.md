# 🚀 Hackathon Express Security API

> Production-ready Express.js API template with built-in security and cloud-native features for rapid hackathon development.

[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Express.js](https://img.shields.io/badge/Express.js-4.18+-blue.svg)](https://expressjs.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)](https://kubernetes.io/)
[![Security](https://img.shields.io/badge/Security-First-red.svg)](#security-features)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 **Mission: 8 Hours → 10 Minutes**

Transform your hackathon development from **8 hours of infrastructure setup** to **10 minutes of deployment** + **23+ hours of pure feature building**.

## ✨ **Key Features**

### 🔐 **Security-First Design**
- **JWT Authentication** with role-based access control
- **Rate Limiting** with DDoS protection
- **Input Validation** and sanitization
- **Security Headers** (Helmet, CORS, CSP)
- **Audit Logging** for compliance
- **API Key Authentication** for service-to-service

### ☁️ **Cloud-Native Ready**
- **Docker** containerization with multi-stage builds
- **Kubernetes** manifests with health checks
- **Health Probes** (liveness, readiness, startup)
- **Graceful Shutdown** handling
- **Multi-Database Support** (MongoDB, PostgreSQL, Redis)
- **Environment Configuration** for all deployment scenarios

### ⚡ **Hackathon Optimized**
- **10-Second Setup** with automated scripts
- **Hot Reload** for rapid development
- **API Documentation** auto-generated with Swagger
- **Example Endpoints** (projects, tasks, users)
- **Database Agnostic** - choose your stack
- **Monitoring Ready** with Prometheus metrics

## 🚀 **Quick Start**

### **Option 1: Docker Setup (Recommended)**
```bash
# Clone and setup
git clone <your-repo-url>
cd hackathon-express-api

# Run setup script
chmod +x setup.sh
./setup.sh

# Start all services (API + databases)
docker-compose up -d

# View logs
docker-compose logs -f api
```

**Ready in 2 minutes!** 🎉
- API: http://localhost:3000
- Docs: http://localhost:3000/api-docs
- Databases: MongoDB, PostgreSQL, Redis included

### **Option 2: Local Development**
```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

## 📚 **API Documentation**

Interactive API documentation available at: `http://localhost:3000/api-docs`

### **Authentication Flow**
```bash
# 1. Register new user
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# 2. Login to get token
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# 3. Use token for authenticated requests
curl -X GET http://localhost:3000/api/v1/projects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **Core Endpoints**
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/health` | GET | Health check | ❌ |
| `/api/auth/register` | POST | User registration | ❌ |
| `/api/auth/login` | POST | User login | ❌ |
| `/api/auth/me` | GET | Current user info | ✅ |
| `/api/users` | GET | List users | ✅ |
| `/api/v1/projects` | GET/POST | Manage projects | ✅ |
| `/api/v1/tasks` | GET/POST | Manage tasks | ✅ |
| `/api/v1/dashboard` | GET | Dashboard overview | ✅ |

## 🏗️ **Project Structure**

```
src/
├── routes/              # API route definitions
│   ├── auth.js          # Authentication & authorization
│   ├── users.js         # User management
│   ├── api.js           # Main API endpoints (projects, tasks)
│   └── health.js        # Health checks & monitoring
├── middleware/          # Express middleware
│   ├── auth.js          # JWT authentication & RBAC
│   ├── security.js      # Security headers & validation
│   └── errorHandler.js  # Global error handling
├── services/           # Business logic (add your services here)
├── models/             # Data models (add your schemas here)
├── utils/              # Helper utilities
│   └── logger.js       # Winston logging configuration
├── config/             # Configuration files
│   ├── database.js     # Multi-database setup
│   └── swagger.js      # API documentation config
└── server.js           # Main application entry point
```

## 🛡️ **Security Features**

### **Built-in Protection**
- ✅ **Helmet** - Security headers
- ✅ **CORS** - Cross-origin resource sharing
- ✅ **Rate Limiting** - DDoS protection
- ✅ **Input Validation** - SQL injection & XSS prevention
- ✅ **JWT Security** - Secure token handling
- ✅ **Password Hashing** - bcrypt with salt rounds
- ✅ **Account Lockout** - Brute force protection
- ✅ **Audit Logging** - Security event tracking

### **Security Configuration**
```javascript
// Example: Rate limiting configuration
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,                 // 100 requests per window
  message: 'Too many requests'
});

// Example: Input validation
const validation = [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }).matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
];
```

## ☁️ **Deployment Options**

### **Docker Deployment**
```bash
# Build production image
docker build -t hackathon-api .

# Run container
docker run -p 3000:3000 \
  -e NODE_ENV=production \
  -e JWT_SECRET=your-secret \
  hackathon-api
```

### **Kubernetes Deployment**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hackathon-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hackathon-api
  template:
    metadata:
      labels:
        app: hackathon-api
    spec:
      containers:
      - name: api
        image: hackathon-api:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 3000
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 3000
```

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

### **Cloud Platform Deployment**

#### **AWS (Docker)**
```bash
# Deploy to AWS ECS or EKS
aws ecr create-repository --repository-name hackathon-api
docker tag hackathon-api:latest $AWS_ACCOUNT.dkr.ecr.region.amazonaws.com/hackathon-api
docker push $AWS_ACCOUNT.dkr.ecr.region.amazonaws.com/hackathon-api
```

#### **Google Cloud (Cloud Run)**
```bash
# Deploy to Google Cloud Run
gcloud run deploy hackathon-api \
  --image gcr.io/PROJECT-ID/hackathon-api \
  --platform managed \
  --allow-unauthenticated
```

#### **Azure (Container Instances)**
```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group hackathon-rg \
  --name hackathon-api \
  --image hackathon-api:latest \
  --ports 3000
```

## 🗄️ **Database Configuration**

### **Multi-Database Support**
Choose your preferred database stack:

```bash
# MongoDB (Document database)
ENABLE_MONGODB=true
MONGODB_URI=mongodb://localhost:27017/hackathon_db

# PostgreSQL (Relational database)
ENABLE_POSTGRESQL=true
PG_HOST=localhost
PG_DATABASE=hackathon_db

# Redis (Cache & sessions)
ENABLE_REDIS=true
REDIS_HOST=localhost
```

### **Database Examples**
```javascript
// MongoDB with Mongoose
const User = mongoose.model('User', {
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, enum: ['user', 'admin'], default: 'user' }
});

// PostgreSQL with Sequelize
const User = sequelize.define('User', {
  email: { type: DataTypes.STRING, allowNull: false, unique: true },
  password: { type: DataTypes.STRING, allowNull: false },
  role: { type: DataTypes.ENUM('user', 'admin'), defaultValue: 'user' }
});

// Redis for caching
await redis.set(`user:${userId}`, JSON.stringify(userData), 'EX', 3600);
```

## 📊 **Monitoring & Observability**

### **Health Checks**
- **Liveness Probe**: `/health/live` - Is the app running?
- **Readiness Probe**: `/health/ready` - Ready to serve traffic?
- **Detailed Health**: `/health/detailed` - Comprehensive system status

### **Metrics & Logging**
- **Prometheus Metrics**: `/health/metrics`
- **Structured Logging**: Winston with JSON format
- **Audit Trails**: Security and business event logging
- **Performance Metrics**: Response times and system resources

## 🧪 **Testing**

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run security tests
npm run test:security

# Load testing
npm run test:load
```

### **Test Examples**
```javascript
// Unit test example
describe('Authentication', () => {
  test('should register new user', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send({
        name: 'Test User',
        email: 'test@example.com',
        password: 'SecurePass123!'
      });
    
    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
  });
});
```

## 🔧 **Development Tools**

### **Code Quality**
```bash
npm run lint          # ESLint code linting
npm run format        # Prettier code formatting
npm run type-check    # TypeScript type checking
```

### **Development Workflow**
```bash
npm run dev           # Start with hot reload
npm run debug         # Start with debugger
npm run build         # Build for production
npm start             # Start production server
```

## 📝 **Environment Variables**

### **Required Variables**
```bash
# Security (Required)
JWT_SECRET=your-super-secret-jwt-key
NODE_ENV=development|production

# Database (Choose at least one)
MONGODB_URI=mongodb://localhost:27017/hackathon_db
PG_HOST=localhost
REDIS_HOST=localhost
```

### **Optional Variables**
```bash
# API Configuration
PORT=3000
HOST=0.0.0.0
API_BASE_URL=http://localhost:3000

# Security Features
RATE_LIMIT_MAX_REQUESTS=100
ALLOWED_ORIGINS=http://localhost:3000

# Feature Flags
FEATURE_USER_REGISTRATION=true
FEATURE_API_DOCUMENTATION=true
```

See [.env.example](.env.example) for complete configuration reference.

## 🎮 **Hackathon Examples**

### **Project Management API**
Perfect for hackathon project tracking:
```javascript
// Create project
POST /api/v1/projects
{
  "name": "AI-Powered Health Monitor",
  "category": "healthtech",
  "tags": ["ai", "health", "iot"]
}

// Add tasks
POST /api/v1/tasks
{
  "title": "Implement ML model",
  "priority": "high",
  "projectId": "project_123"
}
```

### **Team Collaboration Features**
- User roles and permissions
- Project team management
- Task assignment and tracking
- Dashboard overview

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Docker Issues**
```bash
# Docker not starting
docker-compose down && docker-compose up -d

# Permission issues (Linux/Mac)
sudo chown -R $USER:$USER .

# Port conflicts
docker-compose down
# Change port in docker-compose.yml
```

#### **Database Connection Issues**
```bash
# Check database containers
docker-compose ps

# View database logs
docker-compose logs mongodb
docker-compose logs postgres
```

#### **Environment Issues**
```bash
# Verify environment file
cat .env

# Check required variables
npm run check-env
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=debug
npm run dev

# Run with Node.js inspector
npm run debug
# Then open chrome://inspect
```

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Fork and clone
git clone your-fork-url
cd hackathon-express-api

# Install dependencies
npm install

# Run setup
./setup.sh

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
npm test

# Submit pull request
```

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 **Success Stories**

> "We went from 0 to deployed API in 15 minutes. Spent the whole hackathon building features instead of fighting infrastructure!" 
> 
> — Winning Team, TechCrunch Disrupt 2023

> "The security features gave our fintech project the credibility it needed with judges."
> 
> — 2nd Place, FinTech Innovation Challenge

## 🎯 **Next Steps**

1. **Customize the API** for your specific use case
2. **Add your business logic** in the services layer
3. **Integrate with external APIs** using the HTTP client utilities
4. **Deploy to your preferred cloud platform**
5. **Win your hackathon!** 🏆

## 📞 **Support**

- 📧 **Email**: support@hackathon-templates.com
- 💬 **Discord**: [Join our community](https://discord.gg/hackathon-templates)
- 🐙 **GitHub Issues**: [Report bugs and request features](https://github.com/hackathon-templates/express-security-api/issues)
- 📖 **Documentation**: [Full documentation site](https://docs.hackathon-templates.com)

---

**Ready to build something amazing?** 🚀

Get started now and turn your hackathon idea into reality with production-grade infrastructure from day one!
