#!/bin/bash

# Hackathon Express API Setup Script
# Quick setup script for development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project information
PROJECT_NAME="Hackathon Express Security API"
VERSION="1.0.0"

echo -e "${BLUE}🚀 ${PROJECT_NAME} v${VERSION} Setup${NC}"
echo -e "${BLUE}================================================${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js version 18+ required. Current version: $(node -v)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node -v) detected${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ npm $(npm -v) detected${NC}"

# Function to check if Docker is running
check_docker() {
    if command -v docker &> /dev/null && docker info &> /dev/null; then
        echo -e "${GREEN}✅ Docker is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Docker is not running or not installed${NC}"
        return 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose is available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Docker Compose is not available${NC}"
        return 1
    fi
}

# Install dependencies
echo -e "\n${BLUE}📦 Installing dependencies...${NC}"
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n${BLUE}🔧 Creating environment configuration...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Environment file created (.env)${NC}"
    echo -e "${YELLOW}⚠️ Please update .env file with your configuration${NC}"
else
    echo -e "${GREEN}✅ Environment file already exists${NC}"
fi

# Create necessary directories
echo -e "\n${BLUE}📁 Creating project directories...${NC}"
mkdir -p logs uploads temp
echo -e "${GREEN}✅ Directories created${NC}"

# Check Docker setup
echo -e "\n${BLUE}🐳 Checking Docker setup...${NC}"
DOCKER_AVAILABLE=false
DOCKER_COMPOSE_AVAILABLE=false

if check_docker; then
    DOCKER_AVAILABLE=true
    if check_docker_compose; then
        DOCKER_COMPOSE_AVAILABLE=true
    fi
fi

# Run linting and formatting
echo -e "\n${BLUE}🔍 Running code quality checks...${NC}"
npm run lint 2>/dev/null || echo -e "${YELLOW}⚠️ Linting not configured${NC}"
npm run format 2>/dev/null || echo -e "${YELLOW}⚠️ Formatting not configured${NC}"

# Run tests
echo -e "\n${BLUE}🧪 Running tests...${NC}"
npm test 2>/dev/null || echo -e "${YELLOW}⚠️ Tests not available or failed${NC}"

# Display setup completion
echo -e "\n${GREEN}🎉 Setup completed successfully!${NC}"
echo -e "${BLUE}================================================${NC}"

# Display next steps
echo -e "\n${BLUE}📋 Next steps:${NC}"
echo -e "1. ${YELLOW}Update .env file${NC} with your configuration"
echo -e "2. ${YELLOW}Choose your setup method:${NC}"

if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_COMPOSE_AVAILABLE" = true ]; then
    echo -e "\n${GREEN}🐳 Docker Setup (Recommended):${NC}"
    echo -e "   ${BLUE}docker-compose up -d${NC}                    # Start all services"
    echo -e "   ${BLUE}docker-compose logs -f api${NC}              # View API logs"
    echo -e "   ${BLUE}docker-compose down${NC}                     # Stop all services"
fi

echo -e "\n${GREEN}💻 Local Development Setup:${NC}"
echo -e "   ${BLUE}npm run dev${NC}                             # Start development server"
echo -e "   ${BLUE}npm start${NC}                               # Start production server"
echo -e "   ${BLUE}npm test${NC}                                # Run tests"

echo -e "\n${GREEN}🔗 Important URLs (after starting):${NC}"
echo -e "   API Server:      ${BLUE}http://localhost:3000${NC}"
echo -e "   API Docs:        ${BLUE}http://localhost:3000/api-docs${NC}"
echo -e "   Health Check:    ${BLUE}http://localhost:3000/health${NC}"

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "\n${GREEN}🐳 Docker URLs (if using Docker setup):${NC}"
    echo -e "   MongoDB:         ${BLUE}mongodb://localhost:27017${NC}"
    echo -e "   PostgreSQL:      ${BLUE}postgresql://localhost:5432${NC}"
    echo -e "   Redis:           ${BLUE}redis://localhost:6379${NC}"
fi

echo -e "\n${GREEN}📚 Documentation:${NC}"
echo -e "   README.md        - Project overview and instructions"
echo -e "   API Documentation - Interactive docs at /api-docs endpoint"
echo -e "   .env.example     - Complete environment variable reference"

echo -e "\n${GREEN}🛡️ Security Features Enabled:${NC}"
echo -e "   ✅ JWT Authentication"
echo -e "   ✅ Rate Limiting"
echo -e "   ✅ Input Validation"
echo -e "   ✅ Security Headers (Helmet)"
echo -e "   ✅ CORS Protection"
echo -e "   ✅ Audit Logging"

echo -e "\n${GREEN}☁️ Cloud-Native Features:${NC}"
echo -e "   ✅ Docker Containerization"
echo -e "   ✅ Health Checks"
echo -e "   ✅ Graceful Shutdown"
echo -e "   ✅ Environment Configuration"
echo -e "   ✅ Multi-Database Support"

if [ "$DOCKER_AVAILABLE" = false ]; then
    echo -e "\n${YELLOW}💡 Pro Tip: Install Docker for the complete development experience!${NC}"
    echo -e "   Docker provides databases and monitoring out of the box."
fi

echo -e "\n${BLUE}🎯 Ready for your hackathon! Good luck! 🚀${NC}"
echo -e "${BLUE}================================================${NC}"
