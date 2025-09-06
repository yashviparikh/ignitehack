# AI Assistant Instructions - Hackathon Backend Templates

## 🎯 **PROJECT MISSION**
Create production-ready hybrid backend templates combining **Cloud Computing** and **Cybersecurity** for rapid hackathon deployment. Goal: Transform 8 hours of setup into 10 minutes.

## 🚨 **ABSOLUTE RULES - NEVER VIOLATE**
1. **NO INLINE CODE** - Always use external .css/.js/.py/.go files
2. **SCAN BEFORE CODE** - Analyze existing structure before implementing
3. **MODULAR DESIGN** - Small, focused, reusable components only
4. **SECURITY FIRST** - Built-in auth, encryption, validation always
5. **DOCUMENT WORK** - Comprehensive summaries for future AIs

## 🔍 **MANDATORY WORKFLOW**
```
1. SCAN → list_dir(), read_file(), grep_search() existing code
2. PLAN → Provide 2-3 implementation options with trade-offs
3. CODE → Follow modular structure, external files only
4. TEST → Validate security, performance, functionality
5. DOCUMENT → Summarize work for handoff to future AIs
```

## 📂 **PROJECT STRUCTURE**
```
templates/
├── express-api/      # Node.js + Security focus
├── fastapi-cloud/    # Python + Cloud native
├── go-microservice/  # Go + High performance
└── spring-security/  # Java + Enterprise
shared/
├── middleware/       # Auth, security, validation
├── configs/         # Environment settings
├── utils/           # Helper functions
└── docker/          # Containerization
scripts/             # Setup, deploy, test automation
docs/               # Architecture and guides
copilot/            # AI instructions (this file)
```

## 🛡️ **TEMPLATE REQUIREMENTS**
### **Security (Non-negotiable)**
- JWT/OAuth2 authentication
- Input validation & sanitization
- Rate limiting & DDoS protection
- AES-256 encryption for sensitive data
- Audit logging for compliance

### **Cloud-Native (Required)**
- Docker containerization
- Kubernetes manifests
- Health checks (liveness/readiness)
- Auto-scaling configuration
- Environment-based configuration

### **Hackathon-Optimized (Essential)**
- One-command setup script
- Pre-populated sample data
- Auto-generated API documentation
- Real-time monitoring dashboard
- Demo-ready features

## 📋 **CODE ORGANIZATION RULES**
### **File Structure Per Template**
```
template-name/
├── src/
│   ├── routes/       # API endpoints (auth.js, users.js, api.js)
│   ├── middleware/   # Security, validation, logging
│   ├── services/     # Business logic
│   ├── models/       # Data schemas
│   └── utils/        # Helper functions
├── config/           # Environment configurations
├── public/           # Static assets (separate .css/.js files)
├── tests/            # Mirror src/ structure
├── docker/           # Containerization files
└── scripts/          # Setup and deployment
```

### **Quality Standards**
- Functions: <50 lines, Files: <200 lines
- Explicit imports/exports, no circular dependencies
- TypeScript/type hints for all languages
- 80%+ test coverage
- Zero critical security vulnerabilities

## 🤖 **AI COLLABORATION PROTOCOL**
### **Before Starting Work**
- Read these instructions completely
- Scan existing codebase structure
- Check recent git commits for context
- Identify established patterns to follow

### **Work Documentation Template**
```markdown
## Work Summary: [Feature Name]
**Files Modified**: [List with brief descriptions]
**Implementation**: [Approach chosen and why]
**Integration**: [How it connects to existing code]
**Testing**: [Validation performed]
**Future Notes**: [Guidance for next AI]
```

### **Handoff to Future AI**
- Commit work with clear messages
- Update documentation
- Note any unfinished work
- Update these instructions if new patterns emerge

## 🎯 **SUCCESS METRICS**
- **Setup Time**: 0-10 minutes clone to running
- **Security**: Zero critical vulnerabilities
- **Performance**: 1000+ concurrent requests
- **Documentation**: Complete API docs
- **Cloud Deploy**: One-command to production

## 🔧 **IMPLEMENTATION PRIORITIES**
1. **Security middleware** (auth, validation, rate limiting)
2. **Cloud deployment** (Docker, K8s, auto-scaling)
3. **API foundation** (CRUD operations, error handling)
4. **Monitoring** (health checks, metrics, logging)
5. **Hackathon tools** (setup scripts, sample data, docs)

This streamlined guide ensures consistent, high-quality template development across any AI assistant while maintaining security, cloud-readiness, and hackathon optimization.
