/**
 * Custom Security Middleware
 * Additional security layers beyond helmet
 */

const crypto = require('crypto');
const logger = require('../utils/logger');

// Request ID generation for tracking
const generateRequestId = (req, res, next) => {
  req.requestId = crypto.randomUUID();
  res.setHeader('X-Request-ID', req.requestId);
  next();
};

// Security headers middleware
const securityHeaders = (req, res, next) => {
  // Remove server information
  res.removeHeader('X-Powered-By');
  
  // Additional security headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  
  // Cache control for sensitive data
  if (req.path.includes('/api/')) {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
  }
  
  next();
};

// Request logging for security audit
const auditLogger = (req, res, next) => {
  const startTime = Date.now();
  
  // Log request details
  logger.info('Security Audit', {
    requestId: req.requestId,
    method: req.method,
    url: req.originalUrl,
    ip: req.ip || req.connection.remoteAddress,
    userAgent: req.get('User-Agent'),
    timestamp: new Date().toISOString(),
    headers: {
      authorization: req.get('Authorization') ? '[REDACTED]' : undefined,
      contentType: req.get('Content-Type'),
      contentLength: req.get('Content-Length')
    }
  });
  
  // Log response details
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    logger.info('Response Audit', {
      requestId: req.requestId,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      contentLength: res.get('Content-Length')
    });
  });
  
  next();
};

// IP whitelist/blacklist (if configured)
const ipFilter = (req, res, next) => {
  const clientIP = req.ip || req.connection.remoteAddress;
  
  // Check IP blacklist
  const blacklistedIPs = process.env.IP_BLACKLIST?.split(',') || [];
  if (blacklistedIPs.includes(clientIP)) {
    logger.warn('Blocked blacklisted IP', { ip: clientIP, requestId: req.requestId });
    return res.status(403).json({
      error: 'Access denied',
      message: 'Your IP address is not allowed to access this resource'
    });
  }
  
  // Check IP whitelist (if enabled)
  const whitelistedIPs = process.env.IP_WHITELIST?.split(',') || [];
  if (whitelistedIPs.length > 0 && !whitelistedIPs.includes(clientIP)) {
    logger.warn('Blocked non-whitelisted IP', { ip: clientIP, requestId: req.requestId });
    return res.status(403).json({
      error: 'Access denied',
      message: 'Your IP address is not whitelisted for this resource'
    });
  }
  
  next();
};

// Suspicious activity detection
const suspiciousActivityDetector = (req, res, next) => {
  const suspiciousPatterns = [
    /\b(union|select|insert|delete|drop|create|alter)\b/i, // SQL injection
    /<script.*?>.*?<\/script>/i, // XSS attempts
    /\.\.\//g, // Path traversal
    /etc\/passwd/i, // System file access
    /cmd\.exe|powershell/i, // Command injection
  ];
  
  const requestData = JSON.stringify({
    url: req.originalUrl,
    query: req.query,
    body: req.body,
    headers: req.headers
  });
  
  for (const pattern of suspiciousPatterns) {
    if (pattern.test(requestData)) {
      logger.warn('Suspicious activity detected', {
        requestId: req.requestId,
        ip: req.ip,
        pattern: pattern.toString(),
        url: req.originalUrl,
        method: req.method
      });
      
      return res.status(400).json({
        error: 'Invalid request',
        message: 'Request contains potentially malicious content'
      });
    }
  }
  
  next();
};

// Content type validation
const validateContentType = (req, res, next) => {
  if (['POST', 'PUT', 'PATCH'].includes(req.method)) {
    const contentType = req.get('Content-Type');
    
    if (!contentType) {
      return res.status(400).json({
        error: 'Missing Content-Type header',
        message: 'Content-Type header is required for this request method'
      });
    }
    
    const allowedTypes = [
      'application/json',
      'application/x-www-form-urlencoded',
      'multipart/form-data'
    ];
    
    const isValidType = allowedTypes.some(type => contentType.includes(type));
    
    if (!isValidType) {
      return res.status(415).json({
        error: 'Unsupported Media Type',
        message: 'Content-Type not supported',
        supportedTypes: allowedTypes
      });
    }
  }
  
  next();
};

// Combine all security middleware
const securityMiddleware = [
  generateRequestId,
  securityHeaders,
  auditLogger,
  ipFilter,
  suspiciousActivityDetector,
  validateContentType
];

module.exports = securityMiddleware;
