/**
 * Shared Security Configuration
 * Common security settings and utilities for all hackathon templates
 */

const crypto = require('crypto');

// Security constants
const SECURITY_CONSTANTS = {
  // Password requirements
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
  
  // JWT settings
  JWT_ALGORITHM: 'HS256',
  JWT_DEFAULT_EXPIRY: '24h',
  JWT_REFRESH_EXPIRY: '7d',
  
  // Rate limiting
  RATE_LIMIT_WINDOW: 15 * 60 * 1000, // 15 minutes
  RATE_LIMIT_MAX_REQUESTS: 100,
  AUTH_RATE_LIMIT_MAX: 5,
  
  // Security headers
  HSTS_MAX_AGE: 31536000, // 1 year
  
  // Encryption
  ENCRYPTION_ALGORITHM: 'aes-256-gcm',
  KEY_LENGTH: 32,
  IV_LENGTH: 16,
  TAG_LENGTH: 16,
  
  // Session
  SESSION_SECRET_LENGTH: 64,
  
  // API keys
  API_KEY_LENGTH: 32
};

// Default security headers configuration
const SECURITY_HEADERS = {
  helmet: {
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
      maxAge: SECURITY_CONSTANTS.HSTS_MAX_AGE,
      includeSubDomains: true,
      preload: true
    }
  },
  additionalHeaders: {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
  }
};

// CORS configuration
const CORS_CONFIG = {
  development: {
    origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:8080'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'X-API-Key']
  },
  production: {
    origin: process.env.ALLOWED_ORIGINS?.split(',') || false,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization']
  }
};

// Rate limiting configurations
const RATE_LIMIT_CONFIGS = {
  general: {
    windowMs: SECURITY_CONSTANTS.RATE_LIMIT_WINDOW,
    max: SECURITY_CONSTANTS.RATE_LIMIT_MAX_REQUESTS,
    message: {
      error: 'Too many requests from this IP, please try again later.',
      retryAfter: SECURITY_CONSTANTS.RATE_LIMIT_WINDOW
    },
    standardHeaders: true,
    legacyHeaders: false
  },
  auth: {
    windowMs: SECURITY_CONSTANTS.RATE_LIMIT_WINDOW,
    max: SECURITY_CONSTANTS.AUTH_RATE_LIMIT_MAX,
    message: {
      error: 'Too many authentication attempts, please try again later',
      retryAfter: SECURITY_CONSTANTS.RATE_LIMIT_WINDOW
    },
    standardHeaders: true,
    legacyHeaders: false
  },
  passwordReset: {
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 3,
    message: {
      error: 'Too many password reset attempts, please try again later',
      retryAfter: 60 * 60 * 1000
    }
  }
};

/**
 * Generate a secure random string
 */
const generateSecureRandom = (length = 32) => {
  return crypto.randomBytes(length).toString('hex');
};

/**
 * Generate a JWT secret
 */
const generateJWTSecret = () => {
  return generateSecureRandom(64);
};

/**
 * Generate an API key
 */
const generateAPIKey = () => {
  return generateSecureRandom(SECURITY_CONSTANTS.API_KEY_LENGTH);
};

/**
 * Encrypt sensitive data
 */
const encrypt = (text, key) => {
  const algorithm = SECURITY_CONSTANTS.ENCRYPTION_ALGORITHM;
  const iv = crypto.randomBytes(SECURITY_CONSTANTS.IV_LENGTH);
  const cipher = crypto.createCipher(algorithm, key, iv);
  
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  const tag = cipher.getAuthTag();
  
  return {
    encrypted,
    iv: iv.toString('hex'),
    tag: tag.toString('hex')
  };
};

/**
 * Decrypt sensitive data
 */
const decrypt = (encryptedData, key) => {
  const algorithm = SECURITY_CONSTANTS.ENCRYPTION_ALGORITHM;
  const iv = Buffer.from(encryptedData.iv, 'hex');
  const tag = Buffer.from(encryptedData.tag, 'hex');
  
  const decipher = crypto.createDecipher(algorithm, key, iv);
  decipher.setAuthTag(tag);
  
  let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
};

/**
 * Hash sensitive data (one-way)
 */
const hashData = (data, salt = null) => {
  const actualSalt = salt || crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(data, actualSalt, 10000, 64, 'sha512');
  
  return {
    hash: hash.toString('hex'),
    salt: actualSalt
  };
};

/**
 * Verify hashed data
 */
const verifyHash = (data, hash, salt) => {
  const hashedData = crypto.pbkdf2Sync(data, salt, 10000, 64, 'sha512');
  return hashedData.toString('hex') === hash;
};

/**
 * Validate password strength
 */
const validatePassword = (password) => {
  const errors = [];
  
  if (password.length < SECURITY_CONSTANTS.PASSWORD_MIN_LENGTH) {
    errors.push(`Password must be at least ${SECURITY_CONSTANTS.PASSWORD_MIN_LENGTH} characters long`);
  }
  
  if (!SECURITY_CONSTANTS.PASSWORD_PATTERN.test(password)) {
    errors.push('Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Sanitize input to prevent XSS
 */
const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  return input
    .replace(/[<>]/g, '') // Remove < and > characters
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim();
};

/**
 * Validate email format
 */
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Generate Content Security Policy nonce
 */
const generateCSPNonce = () => {
  return crypto.randomBytes(16).toString('base64');
};

/**
 * Security audit logger
 */
const createSecurityAuditLog = (event, details, req = null) => {
  return {
    timestamp: new Date().toISOString(),
    event,
    details,
    ip: req?.ip || null,
    userAgent: req?.get('User-Agent') || null,
    userId: req?.user?.id || null,
    requestId: req?.requestId || null
  };
};

/**
 * Check if IP is in whitelist/blacklist
 */
const checkIPFilter = (ip, whitelist = [], blacklist = []) => {
  // Check blacklist first
  if (blacklist.length > 0 && blacklist.includes(ip)) {
    return { allowed: false, reason: 'IP is blacklisted' };
  }
  
  // Check whitelist (if configured)
  if (whitelist.length > 0 && !whitelist.includes(ip)) {
    return { allowed: false, reason: 'IP is not whitelisted' };
  }
  
  return { allowed: true };
};

/**
 * Security configuration for different environments
 */
const getSecurityConfig = (environment = 'development') => {
  const baseConfig = {
    headers: SECURITY_HEADERS,
    rateLimit: RATE_LIMIT_CONFIGS,
    cors: CORS_CONFIG[environment] || CORS_CONFIG.development,
    jwt: {
      algorithm: SECURITY_CONSTANTS.JWT_ALGORITHM,
      expiresIn: SECURITY_CONSTANTS.JWT_DEFAULT_EXPIRY
    }
  };
  
  if (environment === 'production') {
    // Production-specific security enhancements
    baseConfig.headers.helmet.hsts.preload = true;
    baseConfig.headers.helmet.contentSecurityPolicy.directives.upgradeInsecureRequests = [];
    baseConfig.rateLimit.general.max = 50; // Lower rate limit for production
  }
  
  return baseConfig;
};

module.exports = {
  SECURITY_CONSTANTS,
  SECURITY_HEADERS,
  CORS_CONFIG,
  RATE_LIMIT_CONFIGS,
  generateSecureRandom,
  generateJWTSecret,
  generateAPIKey,
  encrypt,
  decrypt,
  hashData,
  verifyHash,
  validatePassword,
  sanitizeInput,
  validateEmail,
  generateCSPNonce,
  createSecurityAuditLog,
  checkIPFilter,
  getSecurityConfig
};
