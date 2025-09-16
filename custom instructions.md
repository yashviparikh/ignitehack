🤖 AI Assistant Instructions for Hackathon Development
Mission: Create production-ready modular code for 4-person teams in 24 hours

🎯 Core Principles
✅ Essential Rules
Modular Architecture: 4 separate modules, zero conflicts
Windows PowerShell: All automation optimized for Windows
Production-Ready: Deployable code from day one
Test-Driven: Write tests as you develop
Interface-Based: Modules communicate through contracts
🚫 Never Do This
Create monolithic code - Always separate into modules
Skip testing - Test continuously, not at the end
Ignore documentation - Code must be self-documenting
Create tight coupling - Use standardized interfaces
Skip error handling - Robust error management is critical
👥 4-Person Team Structure
Module A: Backend Core (Person 1)
Folder: backend-core/
Focus: API endpoints, authentication, database, security middleware
Start: cd backend-core && .\dev.ps1
Module B: Frontend Core (Person 2)
Folder: frontend-core/
Focus: UI components, state management, routing, API integration
Start: cd frontend-core && .\dev.ps1
Module C: Business Logic (Person 3)
Folder: business-logic/
Focus: Algorithms, data processing, validation, calculations
Start: cd business-logic && .\dev.ps1
Module D: Integration & DevOps (Person 4)
Folder: integration-devops/
Focus: Module integration, deployment, monitoring, CI/CD
Start: cd integration-devops && .\dev.ps1
🔗 Module Communication
// Standardized interface contracts
export const ModuleContracts = {
  BackendAPI: {
    baseUrl: "http://localhost:3000",
    endpoints: { auth: "/api/auth", users: "/api/users", data: "/api/data" }
  },
  BusinessLogic: {
    baseUrl: "http://localhost:3002", 
    endpoints: { process: "/api/process", validate: "/api/validate" }
  },
  HealthCheck: {
    endpoint: "/health",
    format: { status: "healthy|degraded|unhealthy", timestamp: "ISO date" }
  }
};
🛠️ Windows PowerShell Commands
🚀 Quick Start
# Complete team setup (one command)
.\setup-team-workspace.ps1 -FullSetup

# Start all modules for team development
.\start-all-modules.ps1

# Start specific module only
.\start-all-modules.ps1 -Module backend

# Integrate and test all modules
.\integrate-modules.ps1 -Testing

# Deploy to production
.\deploy-production.ps1
⚡ Individual Development
# Backend Core (Person A)
cd backend-core
.\dev.ps1    # Starts API server + tests + hot reload

# Frontend Core (Person B)  
cd frontend-core
.\dev.ps1    # Starts React dev server + tests

# Business Logic (Person C)
cd business-logic
.\dev.ps1    # Starts logic service + performance tests

# Integration & DevOps (Person D)
cd integration-devops
.\dev.ps1    # Starts Docker services + monitoring
🧪 Testing & Quality
Automated Testing Protocol
# Quality gate for each module
function Test-ModuleQuality {
    param([string]$ModulePath)
    Set-Location $ModulePath
    
    # Parallel testing for speed
    $jobs = @()
    $jobs += Start-Job { npm run test }    # Unit tests
    $jobs += Start-Job { npm run lint }    # Code style  
    $jobs += Start-Job { npm audit }       # Security
    
    $results = $jobs | Wait-Job | Receive-Job
    $jobs | Remove-Job
    
    # Must pass all checks
    return ($LASTEXITCODE -eq 0)
}

# Test all modules
$allPassed = @("backend-core", "frontend-core", "business-logic") | 
    ForEach-Object { Test-ModuleQuality $_ } | 
    Where-Object { $_ -eq $false } | Measure-Object | 
    Select-Object -ExpandProperty Count

if ($allPassed -eq 0) {
    Write-Host "🎉 ALL MODULES PASSED!" -ForegroundColor Green
}
Real-Time Health Monitoring
# Continuous quality dashboard
function Start-HealthMonitoring {
    while ($true) {
        Clear-Host
        Write-Host "📊 MODULE HEALTH - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
        
        $modules = @{
            "Backend" = "http://localhost:3000/health"
            "Frontend" = "http://localhost:3001" 
            "Logic" = "http://localhost:3002/health"
            "Integration" = "http://localhost:3003/status"
        }
        
        foreach ($module in $modules.Keys) {
            try {
                $response = Invoke-RestMethod $modules[$module] -TimeoutSec 3
                Write-Host "✅ $module`: Healthy" -ForegroundColor Green
            } catch {
                Write-Host "❌ $module`: Offline" -ForegroundColor Red
            }
        }
        Start-Sleep -Seconds 15
    }
}
💡 Code Quality Standards
Modular Architecture Pattern
// ✅ CORRECT: Independent, testable modules

// backend-core/src/controllers/userController.js
export const UserController = {
  async createUser(req, res) {
    try {
      // Use business logic module for validation
      const validation = await BusinessLogicService.validateUser(req.body);
      if (!validation.valid) {
        return res.status(400).json(ApiResponse.error('Validation failed', validation.errors));
      }
      
      const user = await UserService.create(req.body);
      res.status(201).json(ApiResponse.success(user));
      
    } catch (error) {
      console.error('User creation failed:', error);
      res.status(500).json(ApiResponse.error('Internal server error'));
    }
  }
};

// business-logic/src/validation.js
export const ValidationService = {
  validateUser(userData) {
    const errors = [];
    if (!userData.email || !this.isValidEmail(userData.email)) {
      errors.push('Valid email required');
    }
    if (!userData.password || userData.password.length < 8) {
      errors.push('Password must be 8+ characters');
    }
    return { valid: errors.length === 0, errors };
  }
};
Standardized API Responses
// Standard response format for all APIs
export const ApiResponse = {
  success(data, message = 'Success') {
    return {
      success: true,
      message,
      data,
      timestamp: new Date().toISOString()
    };
  },
  
  error(message, errors = []) {
    return {
      success: false,
      message,
      errors,
      timestamp: new Date().toISOString()
    };
  }
};
Error Handling Pattern
// Comprehensive error handling wrapper
export const SafeAsyncHandler = (fn) => async (req, res, next) => {
  try {
    await fn(req, res, next);
  } catch (error) {
    console.error('API Error:', {
      endpoint: `${req.method} ${req.path}`,
      error: error.message,
      timestamp: new Date().toISOString()
    });
    
    res.status(error.statusCode || 500).json(
      ApiResponse.error(process.env.NODE_ENV === 'production' 
        ? 'Internal server error' 
        : error.message)
    );
  }
};
🚀 Production Deployment
One-Click Deployment
# Complete production deployment
param([switch]$SkipTests)

Write-Host "🚀 Production Deployment..." -ForegroundColor Green

# 1. Pre-deployment validation
if (-not $SkipTests) {
    .\test-integration.ps1
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# 2. Build all modules
@("backend-core", "frontend-core", "business-logic") | ForEach-Object {
    Set-Location $_
    npm run build:prod
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ Build failed: $_"; exit 1 }
    Set-Location ..
}

# 3. Docker deployment
Set-Location integration-devops
docker-compose -f docker-compose.prod.yml up -d

# 4. Health verification
Start-Sleep -Seconds 30
$services = @{
    "Frontend" = "http://localhost:80"
    "Backend" = "http://localhost:3000/health"
    "Logic" = "http://localhost:3002/health"
}

$allHealthy = $true
foreach ($service in $services.Keys) {
    try {
        Invoke-RestMethod $services[$service] -TimeoutSec 10
        Write-Host "✅ $service deployed" -ForegroundColor Green
    } catch {
        Write-Host "❌ $service failed" -ForegroundColor Red
        $allHealthy = $false
    }
}

if ($allHealthy) {
    Write-Host "🎉 DEPLOYMENT SUCCESS! http://localhost" -ForegroundColor Green
} else {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
}
🎯 Quick Reference
Essential Commands
# Setup & Start
.\setup-team-workspace.ps1 -FullSetup     # One-time setup
.\start-all-modules.ps1                   # Start everything

# Individual Development  
cd [module] && .\dev.ps1                  # Start module dev environment

# Testing & Integration
.\test-integration.ps1                    # Test module integration
.\integrate-modules.ps1 -Testing          # Full integration test

# Production
.\deploy-production.ps1                   # Deploy to production
Module URLs
Frontend: http://localhost:3001
Backend API: http://localhost:3000
Business Logic: http://localhost:3002
Integration Dashboard: http://localhost:3003
Success Criteria
✅ All 4 modules run independently
✅ Zero development conflicts between team members
✅ Automated tests pass for all modules
✅ One-click integration and deployment
✅ Production-ready code quality
✅ Working demo within 24 hours
Remember: Simple working code beats complex broken code. Focus on modular, tested solutions! 🏆