# Multi-stage Docker build for production-ready Express API
# Build optimized for security, performance, and minimal image size

# =============================================================================
# BUILD STAGE - Install dependencies and build application
# =============================================================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for building)
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p logs

# =============================================================================
# PRODUCTION STAGE - Create minimal runtime image
# =============================================================================
FROM node:18-alpine AS production

# Add non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Install security updates and runtime dependencies
RUN apk upgrade --no-cache && \
    apk add --no-cache \
    tini \
    curl \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/src ./src
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./
COPY --from=builder --chown=nodejs:nodejs /app/logs ./logs

# Copy additional configuration files
COPY --chown=nodejs:nodejs .env.example ./.env.example

# Create necessary directories and set permissions
RUN mkdir -p /app/uploads /app/temp && \
    chown -R nodejs:nodejs /app && \
    chmod -R 755 /app

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Use tini as entrypoint for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Start the application
CMD ["node", "src/server.js"]

# =============================================================================
# DEVELOPMENT STAGE - Image for development with additional tools
# =============================================================================
FROM node:18-alpine AS development

# Install development tools
RUN apk add --no-cache \
    git \
    curl \
    vim \
    bash

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm install

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads temp

# Expose port
EXPOSE 3000

# Expose debug port
EXPOSE 9229

# Start with nodemon for development
CMD ["npm", "run", "dev"]

# =============================================================================
# METADATA
# =============================================================================
LABEL maintainer="hackathon-templates@example.com"
LABEL description="Production-ready Express.js API with security and cloud-native features"
LABEL version="1.0.0"
LABEL org.opencontainers.image.title="Hackathon Express Security API"
LABEL org.opencontainers.image.description="Express.js API template for hackathons"
LABEL org.opencontainers.image.url="https://github.com/hackathon-templates/express-security-api"
LABEL org.opencontainers.image.source="https://github.com/hackathon-templates/express-security-api"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2023-11-29T10:00:00Z"
LABEL org.opencontainers.image.revision="main"
LABEL org.opencontainers.image.licenses="MIT"
