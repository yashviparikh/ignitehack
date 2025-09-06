/**
 * Hackathon Express Security API Server
 * Production-ready server with built-in security and cloud-native features
 */

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const slowDown = require('express-slow-down');
const mongoSanitize = require('express-mongo-sanitize');
const hpp = require('hpp');
const compression = require('compression');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
require('dotenv').config();

// Import custom middleware and configs
const logger = require('./utils/logger');
const errorHandler = require('./middleware/errorHandler');
const authMiddleware = require('./middleware/auth');
const securityMiddleware = require('./middleware/security');
const config = require('./config/database');

// Import routes
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const apiRoutes = require('./routes/api');
const healthRoutes = require('./routes/health');

// Initialize Express app
const app = express();

// Security middleware - First priority
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      objectSrc: ["'none'"],
      upgradeInsecureRequests: [],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

// Rate limiting - DDoS protection
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: 15 * 60 * 1000
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Speed limiting for additional protection
const speedLimiter = slowDown({
  windowMs: 15 * 60 * 1000, // 15 minutes
  delayAfter: 50, // Allow 50 requests per windowMs without delay
  delayMs: 500 // Add 500ms delay per request after delayAfter
});

app.use(limiter);
app.use(speedLimiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(cookieParser());

// Data sanitization
app.use(mongoSanitize()); // Against NoSQL injection
app.use(hpp()); // Prevent parameter pollution

// Compression for better performance
app.use(compression());

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Logging
if (process.env.NODE_ENV === 'production') {
  app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));
} else {
  app.use(morgan('dev'));
}

// Custom security middleware
app.use(securityMiddleware);

// Health check routes (before auth)
app.use('/health', healthRoutes);

// API Documentation
if (process.env.NODE_ENV !== 'production') {
  const swaggerUi = require('swagger-ui-express');
  const swaggerSpec = require('./config/swagger');
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
}

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/users', authMiddleware, userRoutes);
app.use('/api/v1', authMiddleware, apiRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.status(200).json({
    message: 'Hackathon Express Security API',
    version: '1.0.0',
    status: 'running',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    endpoints: {
      health: '/health',
      auth: '/api/auth',
      users: '/api/users',
      api: '/api/v1',
      docs: process.env.NODE_ENV !== 'production' ? '/api-docs' : 'disabled'
    }
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route not found',
    message: `The requested endpoint ${req.originalUrl} does not exist`,
    availableEndpoints: ['/health', '/api/auth', '/api/users', '/api/v1']
  });
});

// Global error handler (must be last)
app.use(errorHandler);

// Graceful shutdown handling
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Uncaught exception handler
process.on('uncaughtException', (err) => {
  logger.error('Uncaught Exception:', err);
  process.exit(1);
});

// Unhandled promise rejection handler
process.on('unhandledRejection', (err) => {
  logger.error('Unhandled Promise Rejection:', err);
  process.exit(1);
});

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

const server = app.listen(PORT, HOST, () => {
  logger.info(`🚀 Hackathon API Server running on ${HOST}:${PORT}`);
  logger.info(`📚 API Documentation: http://${HOST}:${PORT}/api-docs`);
  logger.info(`❤️ Health Check: http://${HOST}:${PORT}/health`);
  logger.info(`🔒 Security: Rate limiting, CORS, Helmet enabled`);
  logger.info(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = { app, server };
