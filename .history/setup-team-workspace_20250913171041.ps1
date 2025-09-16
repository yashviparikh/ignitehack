# ✅ COMPLETE Team Workspace Setup for 4-Person Hackathon
# Windows PowerShell automation script for modular development

param(
    [string]$TeamName = "Hackathon-Team",
    [string]$ProjectPath = "C:\Probz\Hackathon",
    [switch]$FullSetup,
    [switch]$ModulesOnly
)

Write-Host "🚀 Setting up 4-Person Modular Hackathon Workspace..." -ForegroundColor Green
Write-Host "Team: $TeamName" -ForegroundColor Cyan
Write-Host "Path: $ProjectPath" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Green

# Ensure we're in the project directory
Set-Location $ProjectPath

# Step 1: Create Module Directory Structure
Write-Host "1️⃣ Creating modular directory structure..." -ForegroundColor Yellow

$moduleStructure = @{
    "backend-core" = @(
        "src/controllers",
        "src/services", 
        "src/models",
        "src/middleware",
        "src/routes",
        "src/config",
        "src/interfaces",
        "tests/unit",
        "tests/integration",
        "docs"
    )
    "frontend-core" = @(
        "src/components",
        "src/hooks",
        "src/pages",
        "src/services",
        "src/utils",
        "src/types",
        "public/assets",
        "tests/components",
        "tests/integration",
        "docs"
    )
    "business-logic" = @(
        "src/algorithms",
        "src/validators", 
        "src/processors",
        "src/interfaces",
        "src/types",
        "tests/unit",
        "tests/performance",
        "docs"
    )
    "integration-devops" = @(
        "src/monitoring",
        "src/deployment",
        "src/orchestration",
        "docker",
        "scripts",
        "config",
        "tests/integration",
        "docs"
    )
}

foreach ($module in $moduleStructure.Keys) {
    Write-Host "   📁 Creating $module module..." -ForegroundColor Gray
    
    # Create main module directory
    if (-not (Test-Path $module)) {
        New-Item -ItemType Directory -Path $module -Force | Out-Null
    }
    
    # Create subdirectories
    foreach ($subDir in $moduleStructure[$module]) {
        $fullPath = Join-Path $module $subDir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }
    }
}

# Step 2: Generate Module-Specific package.json files
Write-Host "2️⃣ Generating module package configurations..." -ForegroundColor Yellow

# Backend Core package.json
$backendPackage = @{
    name = "hackathon-backend-core"
    version = "1.0.0"
    description = "Backend Core Module - Person A"
    main = "src/server.js"
    scripts = @{
        "start" = "node src/server.js"
        "start:prod" = "NODE_ENV=production node src/server.js"
        "dev" = "nodemon src/server.js"
        "test" = "jest"
        "test:watch" = "jest --watch"
        "test:coverage" = "jest --coverage"
        "lint" = "eslint src/"
        "lint:fix" = "eslint src/ --fix"
        "build" = "npm run lint && npm run test"
        "build:prod" = "npm run build && npm run test:coverage"
        "security:scan" = "npm audit"
        "type:check" = "echo 'No TypeScript in this module'"
        "contracts:validate" = "node scripts/validate-contracts.js"
    }
    dependencies = @{
        "express" = "^4.18.2"
        "cors" = "^2.8.5"
        "helmet" = "^7.0.0"
        "morgan" = "^1.10.0"
        "dotenv" = "^16.0.3"
        "joi" = "^17.9.2"
        "bcrypt" = "^5.1.0"
        "jsonwebtoken" = "^9.0.0"
        "compression" = "^1.7.4"
        "express-rate-limit" = "^6.7.0"
    }
    devDependencies = @{
        "nodemon" = "^2.0.22"
        "jest" = "^29.5.0"
        "supertest" = "^6.3.3"
        "eslint" = "^8.40.0"
    }
}

$backendPackage | ConvertTo-Json -Depth 10 | Out-File "backend-core/package.json" -Encoding UTF8

# Frontend Core package.json
$frontendPackage = @{
    name = "hackathon-frontend-core"
    version = "1.0.0"
    description = "Frontend Core Module - Person B"
    private = $true
    scripts = @{
        "start" = "react-scripts start"
        "build" = "react-scripts build"
        "build:prod" = "CI=true npm run build"
        "test" = "react-scripts test --watchAll=false"
        "test:watch" = "react-scripts test"
        "test:coverage" = "react-scripts test --coverage --watchAll=false"
        "test:components" = "npm run test -- --testPathPattern=components"
        "test:hooks" = "npm run test -- --testPathPattern=hooks"
        "test:integration" = "npm run test -- --testPathPattern=integration"
        "lint" = "eslint src/"
        "lint:fix" = "eslint src/ --fix"
        "a11y:test" = "npm run build && npx @axe-core/cli ./build"
        "eject" = "react-scripts eject"
    }
    dependencies = @{
        "react" = "^18.2.0"
        "react-dom" = "^18.2.0"
        "react-router-dom" = "^6.11.0"
        "axios" = "^1.4.0"
        "styled-components" = "^6.0.0"
        "react-query" = "^3.39.3"
        "react-hook-form" = "^7.43.9"
        "react-hot-toast" = "^2.4.1"
    }
    devDependencies = @{
        "react-scripts" = "5.0.1"
        "@testing-library/react" = "^13.4.0"
        "@testing-library/jest-dom" = "^5.16.5"
        "@testing-library/user-event" = "^14.4.3"
        "eslint" = "^8.40.0"
        "@axe-core/cli" = "^4.7.0"
    }
    browserslist = @{
        production = @(
            ">0.2%",
            "not dead",
            "not op_mini all"
        )
        development = @(
            "last 1 chrome version",
            "last 1 firefox version",
            "last 1 safari version"
        )
    }
}

$frontendPackage | ConvertTo-Json -Depth 10 | Out-File "frontend-core/package.json" -Encoding UTF8

# Business Logic package.json
$businessPackage = @{
    name = "hackathon-business-logic"
    version = "1.0.0"
    description = "Business Logic Module - Person C"
    main = "src/index.js"
    scripts = @{
        "start" = "node src/index.js"
        "start:service" = "node src/service.js"
        "dev" = "nodemon src/index.js"
        "test" = "jest"
        "test:watch" = "jest --watch"
        "test:algorithms" = "jest --testPathPattern=algorithms"
        "test:performance" = "jest --testPathPattern=performance"
        "test:validation" = "jest --testPathPattern=validation"
        "test:coverage" = "jest --coverage"
        "lint" = "eslint src/"
        "lint:fix" = "eslint src/ --fix"
        "docs:validate" = "jsdoc-to-markdown src/**/*.js --dry-run"
        "complexity:check" = "npx complexity-report src/"
        "build" = "npm run lint && npm run test"
    }
    dependencies = @{
        "lodash" = "^4.17.21"
        "moment" = "^2.29.4"
        "validator" = "^13.9.0"
        "joi" = "^17.9.2"
        "crypto" = "^1.0.1"
        "uuid" = "^9.0.0"
    }
    devDependencies = @{
        "jest" = "^29.5.0"
        "nodemon" = "^2.0.22"
        "eslint" = "^8.40.0"
        "jsdoc-to-markdown" = "^8.0.0"
        "complexity-report" = "^2.0.0-alpha"
    }
}

$businessPackage | ConvertTo-Json -Depth 10 | Out-File "business-logic/package.json" -Encoding UTF8

# Integration DevOps package.json
$integrationPackage = @{
    name = "hackathon-integration-devops"
    version = "1.0.0"
    description = "Integration & DevOps Module - Person D"
    main = "src/orchestrator.js"
    scripts = @{
        "start" = "node src/orchestrator.js"
        "start:monitor" = "node src/monitoring/health-monitor.js"
        "dev" = "nodemon src/orchestrator.js"
        "test" = "jest"
        "test:integration" = "jest --testPathPattern=integration"
        "test:deployment" = "jest --testPathPattern=deployment"
        "test:monitoring" = "jest --testPathPattern=monitoring"
        "lint" = "eslint src/"
        "build" = "npm run lint && npm run test"
        "docker:build" = "docker-compose build"
        "docker:up" = "docker-compose up -d"
        "docker:down" = "docker-compose down"
        "deploy:local" = "node scripts/deploy-local.js"
        "deploy:prod" = "node scripts/deploy-production.js"
    }
    dependencies = @{
        "express" = "^4.18.2"
        "dockerode" = "^3.3.5"
        "node-cron" = "^3.0.2"
        "axios" = "^1.4.0"
        "winston" = "^3.8.2"
        "prometheus-client" = "^14.2.0"
    }
    devDependencies = @{
        "jest" = "^29.5.0"
        "nodemon" = "^2.0.22"
        "eslint" = "^8.40.0"
    }
}

$integrationPackage | ConvertTo-Json -Depth 10 | Out-File "integration-devops/package.json" -Encoding UTF8

# Step 3: Create Module Interface Contracts
Write-Host "3️⃣ Creating module interface contracts..." -ForegroundColor Yellow

# Backend Core interfaces
$backendContract = @{
    version = "1.0.0"
    module = "backend-core"
    exposedAPIs = @{
        authentication = @{
            endpoints = @(
                @{ method = "POST"; path = "/api/auth/login"; description = "User login" },
                @{ method = "POST"; path = "/api/auth/register"; description = "User registration" },
                @{ method = "POST"; path = "/api/auth/logout"; description = "User logout" }
            )
        }
        users = @{
            endpoints = @(
                @{ method = "GET"; path = "/api/users"; description = "Get all users" },
                @{ method = "GET"; path = "/api/users/:id"; description = "Get user by ID" },
                @{ method = "PUT"; path = "/api/users/:id"; description = "Update user" }
            )
        }
        health = @{
            endpoints = @(
                @{ method = "GET"; path = "/health"; description = "Health check" }
            )
        }
    }
    consumedAPIs = @{
        businessLogic = @{
            baseUrl = "http://localhost:3002"
            endpoints = @("/api/validate", "/api/process")
        }
    }
    events = @{
        emits = @("user.created", "user.updated", "auth.login")
        listens = @("business.validation.result")
    }
}

$backendContract | ConvertTo-Json -Depth 10 | Out-File "backend-core/src/interfaces/contracts.json" -Encoding UTF8

# Frontend Core interfaces
$frontendContract = @{
    version = "1.0.0"
    module = "frontend-core"
    exposedComponents = @{
        authentication = @("LoginForm", "RegisterForm", "AuthGuard")
        common = @("Button", "Input", "Modal", "Loader")
        layout = @("Header", "Footer", "Sidebar", "Layout")
    }
    consumedAPIs = @{
        backend = @{
            baseUrl = "http://localhost:3000"
            endpoints = @("/api/auth/*", "/api/users/*", "/health")
        }
        businessLogic = @{
            baseUrl = "http://localhost:3002"
            endpoints = @("/api/calculate/*", "/api/validate/*")
        }
    }
    routes = @{
        public = @("/", "/login", "/register")
        protected = @("/dashboard", "/profile", "/settings")
    }
}

$frontendContract | ConvertTo-Json -Depth 10 | Out-File "frontend-core/src/interfaces/contracts.json" -Encoding UTF8

# Business Logic interfaces
$businessContract = @{
    version = "1.0.0"
    module = "business-logic"
    exposedAPIs = @{
        validation = @{
            endpoints = @(
                @{ method = "POST"; path = "/api/validate/user"; description = "Validate user data" },
                @{ method = "POST"; path = "/api/validate/business"; description = "Validate business rules" }
            )
        }
        processing = @{
            endpoints = @(
                @{ method = "POST"; path = "/api/process/data"; description = "Process data" },
                @{ method = "GET"; path = "/api/calculate/:type"; description = "Perform calculations" }
            )
        }
        health = @{
            endpoints = @(
                @{ method = "GET"; path = "/health"; description = "Health check" }
            )
        }
    }
    algorithms = @{
        available = @("sorting", "searching", "validation", "encryption", "calculation")
        performance = @{
            maxProcessingTime = "5000ms"
            maxMemoryUsage = "100MB"
        }
    }
}

$businessContract | ConvertTo-Json -Depth 10 | Out-File "business-logic/src/interfaces/contracts.json" -Encoding UTF8

# Integration DevOps interfaces
$integrationContract = @{
    version = "1.0.0"
    module = "integration-devops"
    exposedAPIs = @{
        monitoring = @{
            endpoints = @(
                @{ method = "GET"; path = "/status"; description = "System status" },
                @{ method = "GET"; path = "/metrics"; description = "System metrics" },
                @{ method = "GET"; path = "/health/all"; description = "All modules health" }
            )
        }
        deployment = @{
            endpoints = @(
                @{ method = "POST"; path = "/deploy"; description = "Trigger deployment" },
                @{ method = "GET"; path = "/deploy/status"; description = "Deployment status" }
            )
        }
    }
    monitoredServices = @(
        @{ name = "backend-core"; port = 3000; healthEndpoint = "/health" },
        @{ name = "frontend-core"; port = 3001; healthEndpoint = "/" },
        @{ name = "business-logic"; port = 3002; healthEndpoint = "/health" }
    )
    deploymentTargets = @("local", "development", "staging", "production")
}

$integrationContract | ConvertTo-Json -Depth 10 | Out-File "integration-devops/src/interfaces/contracts.json" -Encoding UTF8

# Step 4: Create Individual Development Scripts
Write-Host "4️⃣ Creating individual development scripts..." -ForegroundColor Yellow

# Backend Core dev script
$backendDevScript = @'
# Backend Core Development Script - Person A
# backend-core/dev.ps1

Write-Host "🏗️ Starting Backend Core Development Environment..." -ForegroundColor Green

# Check prerequisites
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start development server with hot reload
Write-Host "🚀 Starting development server on port 3000..." -ForegroundColor Cyan
Write-Host "📝 API Documentation: http://localhost:3000/docs" -ForegroundColor Gray
Write-Host "🔍 Health Check: http://localhost:3000/health" -ForegroundColor Gray

# Run in parallel: server, tests, linting
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev
} -Name "BackendServer"

Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Start-Sleep -Seconds 5
    npm run test:watch
} -Name "BackendTests"

Write-Host "✅ Backend Core development environment ready!" -ForegroundColor Green
Write-Host "📊 Test results will appear below..." -ForegroundColor Gray

# Keep the main script running
try {
    while ($true) {
        Start-Sleep -Seconds 10
        # Check if server is still running
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:3000/health" -TimeoutSec 3
            Write-Host "💚 Backend Core: $($response.status) - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
        } catch {
            Write-Host "💔 Backend Core: Unhealthy - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Red
        }
    }
} finally {
    Get-Job | Stop-Job
    Get-Job | Remove-Job
}
'@
$backendDevScript | Out-File "backend-core/dev.ps1" -Encoding UTF8

# Frontend Core dev script
$frontendDevScript = @'
# Frontend Core Development Script - Person B
# frontend-core/dev.ps1

Write-Host "🎨 Starting Frontend Core Development Environment..." -ForegroundColor Blue

# Check prerequisites
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start development server
Write-Host "🚀 Starting React development server on port 3001..." -ForegroundColor Cyan
Write-Host "🌐 Application: http://localhost:3001" -ForegroundColor Gray
Write-Host "🔧 Component Tests: npm run test:components" -ForegroundColor Gray

# Set React dev server port
$env:PORT = "3001"

# Run in parallel: React server, tests
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    $env:PORT = "3001"
    npm start
} -Name "ReactServer"

Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Start-Sleep -Seconds 10
    npm run test:watch
} -Name "ReactTests"

Write-Host "✅ Frontend Core development environment ready!" -ForegroundColor Green
Write-Host "📊 Test results and hot reload active..." -ForegroundColor Gray

# Keep the main script running
try {
    while ($true) {
        Start-Sleep -Seconds 15
        # Check if React server is running
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3001" -TimeoutSec 3
            $status = if ($response.StatusCode -eq 200) { "Healthy" } else { "Unhealthy" }
            Write-Host "💙 Frontend Core: $status - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Blue
        } catch {
            Write-Host "💔 Frontend Core: Unhealthy - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Red
        }
    }
} finally {
    Get-Job | Stop-Job
    Get-Job | Remove-Job
}
'@
$frontendDevScript | Out-File "frontend-core/dev.ps1" -Encoding UTF8

# Business Logic dev script
$businessDevScript = @'
# Business Logic Development Script - Person C
# business-logic/dev.ps1

Write-Host "💼 Starting Business Logic Development Environment..." -ForegroundColor Magenta

# Check prerequisites
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start service
Write-Host "🚀 Starting Business Logic service on port 3002..." -ForegroundColor Cyan
Write-Host "🧮 Algorithms: http://localhost:3002/api/calculate" -ForegroundColor Gray
Write-Host "✅ Validation: http://localhost:3002/api/validate" -ForegroundColor Gray

# Run in parallel: service, tests, performance monitoring
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev
} -Name "BusinessLogicService"

Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Start-Sleep -Seconds 5
    npm run test:watch
} -Name "BusinessLogicTests"

Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Start-Sleep -Seconds 10
    # Run performance tests every 30 seconds
    while ($true) {
        npm run test:performance --silent
        Start-Sleep -Seconds 30
    }
} -Name "PerformanceMonitor"

Write-Host "✅ Business Logic development environment ready!" -ForegroundColor Green
Write-Host "📊 Algorithm performance monitoring active..." -ForegroundColor Gray

# Keep the main script running
try {
    while ($true) {
        Start-Sleep -Seconds 12
        # Check service health
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:3002/health" -TimeoutSec 3
            Write-Host "💜 Business Logic: $($response.status) - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Magenta
        } catch {
            Write-Host "💔 Business Logic: Unhealthy - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Red
        }
    }
} finally {
    Get-Job | Stop-Job
    Get-Job | Remove-Job
}
'@
$businessDevScript | Out-File "business-logic/dev.ps1" -Encoding UTF8

# Integration DevOps dev script
$integrationDevScript = @'
# Integration & DevOps Development Script - Person D
# integration-devops/dev.ps1

Write-Host "🔧 Starting Integration & DevOps Environment..." -ForegroundColor DarkYellow

# Check prerequisites
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start infrastructure services
Write-Host "🐳 Starting Docker services..." -ForegroundColor Cyan
docker-compose up -d postgres redis

# Start monitoring service
Write-Host "🚀 Starting monitoring service on port 3003..." -ForegroundColor Cyan
Write-Host "📊 Dashboard: http://localhost:3003/status" -ForegroundColor Gray
Write-Host "📈 Metrics: http://localhost:3003/metrics" -ForegroundColor Gray

# Run monitoring and orchestration
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev
} -Name "MonitoringService"

Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Start-Sleep -Seconds 5
    npm run test:watch
} -Name "IntegrationTests"

# Start health monitoring for all modules
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Start-Sleep -Seconds 10
    
    while ($true) {
        Write-Host "🔍 Module Health Check - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow
        
        # Check all modules
        $modules = @(
            @{ Name = "Backend"; Port = 3000; Endpoint = "/health" },
            @{ Name = "Frontend"; Port = 3001; Endpoint = "/" },
            @{ Name = "Business Logic"; Port = 3002; Endpoint = "/health" },
            @{ Name = "Integration"; Port = 3003; Endpoint = "/status" }
        )
        
        foreach ($module in $modules) {
            try {
                if ($module.Endpoint -eq "/") {
                    $response = Invoke-WebRequest -Uri "http://localhost:$($module.Port)" -TimeoutSec 3
                    $status = if ($response.StatusCode -eq 200) { "✅ Healthy" } else { "❌ Unhealthy" }
                } else {
                    $response = Invoke-RestMethod -Uri "http://localhost:$($module.Port)$($module.Endpoint)" -TimeoutSec 3
                    $status = "✅ Healthy"
                }
                Write-Host "   $($module.Name): $status" -ForegroundColor Green
            } catch {
                Write-Host "   $($module.Name): ❌ Unhealthy" -ForegroundColor Red
            }
        }
        
        Write-Host ""
        Start-Sleep -Seconds 30
    }
} -Name "HealthMonitor"

Write-Host "✅ Integration & DevOps environment ready!" -ForegroundColor Green
Write-Host "📊 Monitoring all modules..." -ForegroundColor Gray

# Keep the main script running
try {
    while ($true) {
        Start-Sleep -Seconds 20
        # Check monitoring service
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:3003/status" -TimeoutSec 3
            Write-Host "🔧 Integration & DevOps: Monitoring Active - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor DarkYellow
        } catch {
            Write-Host "💔 Integration & DevOps: Unhealthy - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Red
        }
    }
} finally {
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    docker-compose down
}
'@
$integrationDevScript | Out-File "integration-devops/dev.ps1" -Encoding UTF8

# Step 5: Create Master Control Script
Write-Host "5️⃣ Creating master control script..." -ForegroundColor Yellow

$masterScript = @'
# Master Development Control Script
# start-all-modules.ps1 - Controls all 4 modules

param(
    [string]$Module = "all",
    [switch]$Production,
    [switch]$TestMode
)

Write-Host "🎮 HACKATHON DEVELOPMENT CONTROL CENTER" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

if ($Module -eq "all") {
    Write-Host "🚀 Starting ALL modules for 4-person team..." -ForegroundColor Green
    
    # Start each module in separate PowerShell windows
    Write-Host "1️⃣ Starting Backend Core (Person A)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'backend-core'; .\dev.ps1"
    Start-Sleep -Seconds 3
    
    Write-Host "2️⃣ Starting Frontend Core (Person B)..." -ForegroundColor Yellow  
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'frontend-core'; .\dev.ps1"
    Start-Sleep -Seconds 3
    
    Write-Host "3️⃣ Starting Business Logic (Person C)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'business-logic'; .\dev.ps1"
    Start-Sleep -Seconds 3
    
    Write-Host "4️⃣ Starting Integration & DevOps (Person D)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'integration-devops'; .\dev.ps1"
    
    Write-Host "✅ All modules starting in separate windows!" -ForegroundColor Green
    Write-Host "🌐 URLs will be available in ~30 seconds:" -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:3001" -ForegroundColor Gray
    Write-Host "   Backend API: http://localhost:3000" -ForegroundColor Gray  
    Write-Host "   Business Logic: http://localhost:3002" -ForegroundColor Gray
    Write-Host "   Monitoring: http://localhost:3003" -ForegroundColor Gray
    
} elseif ($Module -eq "backend") {
    Write-Host "🏗️ Starting Backend Core only..." -ForegroundColor Green
    Set-Location "backend-core"
    .\dev.ps1
    
} elseif ($Module -eq "frontend") {
    Write-Host "🎨 Starting Frontend Core only..." -ForegroundColor Blue
    Set-Location "frontend-core"
    .\dev.ps1
    
} elseif ($Module -eq "business") {
    Write-Host "💼 Starting Business Logic only..." -ForegroundColor Magenta
    Set-Location "business-logic"
    .\dev.ps1
    
} elseif ($Module -eq "integration") {
    Write-Host "🔧 Starting Integration & DevOps only..." -ForegroundColor DarkYellow
    Set-Location "integration-devops"
    .\dev.ps1
    
} else {
    Write-Host "❌ Invalid module. Use: all, backend, frontend, business, integration" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Development environment ready for hackathon!" -ForegroundColor Green
'@
$masterScript | Out-File "start-all-modules.ps1" -Encoding UTF8

# Step 6: Install Dependencies (if FullSetup)
if ($FullSetup) {
    Write-Host "6️⃣ Installing dependencies for all modules..." -ForegroundColor Yellow
    
    $modules = @("backend-core", "frontend-core", "business-logic", "integration-devops")
    
    foreach ($module in $modules) {
        Write-Host "   📦 Installing $module dependencies..." -ForegroundColor Gray
        Set-Location $module
        npm install --silent
        Set-Location ..
    }
}

# Final Success Message
Write-Host "" 
Write-Host "🎉 4-PERSON HACKATHON WORKSPACE SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "👥 Team Member Assignments:" -ForegroundColor Cyan
Write-Host "   Person A: Backend Core (backend-core/)" -ForegroundColor Yellow
Write-Host "   Person B: Frontend Core (frontend-core/)" -ForegroundColor Blue  
Write-Host "   Person C: Business Logic (business-logic/)" -ForegroundColor Magenta
Write-Host "   Person D: Integration & DevOps (integration-devops/)" -ForegroundColor DarkYellow
Write-Host ""
Write-Host "🚀 Quick Start Commands:" -ForegroundColor Cyan
Write-Host "   Start all modules: .\start-all-modules.ps1" -ForegroundColor Gray
Write-Host "   Start specific module: .\start-all-modules.ps1 -Module backend" -ForegroundColor Gray
Write-Host "   Install dependencies: .\setup-team-workspace.ps1 -FullSetup" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   Team Plan: copilot\plan.md" -ForegroundColor Gray
Write-Host "   AI Instructions: copilot\ai-assistant-instructions.md" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Ready for parallel development!" -ForegroundColor Green
