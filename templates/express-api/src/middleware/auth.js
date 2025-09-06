/**
 * Authentication Middleware
 * JWT-based authentication with role-based access control
 */

const jwt = require('jsonwebtoken');
const logger = require('../utils/logger');

// JWT secret from environment
const JWT_SECRET = process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h';

/**
 * Generate JWT token
 */
const generateToken = (payload) => {
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: JWT_EXPIRES_IN,
    issuer: 'hackathon-api',
    audience: 'hackathon-users'
  });
};

/**
 * Verify JWT token
 */
const verifyToken = (token) => {
  try {
    return jwt.verify(token, JWT_SECRET, {
      issuer: 'hackathon-api',
      audience: 'hackathon-users'
    });
  } catch (error) {
    throw new Error(`Token verification failed: ${error.message}`);
  }
};

/**
 * Authentication middleware
 */
const authenticate = async (req, res, next) => {
  try {
    // Get token from header
    const authHeader = req.headers.authorization;
    
    if (!authHeader) {
      return res.status(401).json({
        error: 'Authentication required',
        message: 'No authorization header provided'
      });
    }
    
    // Check if header starts with Bearer
    if (!authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'Invalid token format',
        message: 'Authorization header must start with "Bearer "'
      });
    }
    
    // Extract token
    const token = authHeader.substring(7);
    
    if (!token) {
      return res.status(401).json({
        error: 'Token missing',
        message: 'No token provided in authorization header'
      });
    }
    
    // Verify token
    const decoded = verifyToken(token);
    
    // Add user info to request
    req.user = {
      id: decoded.userId,
      email: decoded.email,
      role: decoded.role,
      permissions: decoded.permissions || [],
      tokenIat: decoded.iat,
      tokenExp: decoded.exp
    };
    
    // Log successful authentication
    logger.info('User authenticated', {
      requestId: req.requestId,
      userId: req.user.id,
      email: req.user.email,
      role: req.user.role
    });
    
    next();
    
  } catch (error) {
    logger.warn('Authentication failed', {
      requestId: req.requestId,
      error: error.message,
      ip: req.ip
    });
    
    return res.status(401).json({
      error: 'Authentication failed',
      message: 'Invalid or expired token'
    });
  }
};

/**
 * Optional authentication (doesn't fail if no token)
 */
const optionalAuth = async (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (authHeader && authHeader.startsWith('Bearer ')) {
    try {
      const token = authHeader.substring(7);
      const decoded = verifyToken(token);
      
      req.user = {
        id: decoded.userId,
        email: decoded.email,
        role: decoded.role,
        permissions: decoded.permissions || []
      };
    } catch (error) {
      // Token invalid but continue without user
      logger.debug('Optional auth failed', { error: error.message });
    }
  }
  
  next();
};

/**
 * Role-based authorization middleware
 */
const authorize = (allowedRoles = []) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication required',
        message: 'User must be authenticated to access this resource'
      });
    }
    
    // Check if user has required role
    if (allowedRoles.length > 0 && !allowedRoles.includes(req.user.role)) {
      logger.warn('Authorization failed', {
        requestId: req.requestId,
        userId: req.user.id,
        userRole: req.user.role,
        requiredRoles: allowedRoles
      });
      
      return res.status(403).json({
        error: 'Insufficient permissions',
        message: `Access denied. Required roles: ${allowedRoles.join(', ')}`
      });
    }
    
    next();
  };
};

/**
 * Permission-based authorization middleware
 */
const requirePermission = (requiredPermission) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication required',
        message: 'User must be authenticated to access this resource'
      });
    }
    
    // Check if user has required permission
    if (!req.user.permissions.includes(requiredPermission)) {
      logger.warn('Permission denied', {
        requestId: req.requestId,
        userId: req.user.id,
        userPermissions: req.user.permissions,
        requiredPermission
      });
      
      return res.status(403).json({
        error: 'Permission denied',
        message: `Access denied. Required permission: ${requiredPermission}`
      });
    }
    
    next();
  };
};

/**
 * Resource ownership check
 */
const requireOwnership = (resourceIdParam = 'id') => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication required',
        message: 'User must be authenticated to access this resource'
      });
    }
    
    const resourceId = req.params[resourceIdParam];
    const userId = req.user.id;
    
    // Admin can access any resource
    if (req.user.role === 'admin') {
      return next();
    }
    
    // Check if user owns the resource
    if (resourceId !== userId) {
      logger.warn('Ownership check failed', {
        requestId: req.requestId,
        userId,
        resourceId,
        resourceParam: resourceIdParam
      });
      
      return res.status(403).json({
        error: 'Access denied',
        message: 'You can only access your own resources'
      });
    }
    
    next();
  };
};

/**
 * API key authentication (for service-to-service communication)
 */
const authenticateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  const validApiKeys = process.env.API_KEYS?.split(',') || [];
  
  if (!apiKey) {
    return res.status(401).json({
      error: 'API key required',
      message: 'X-API-Key header is required'
    });
  }
  
  if (!validApiKeys.includes(apiKey)) {
    logger.warn('Invalid API key attempt', {
      requestId: req.requestId,
      ip: req.ip,
      providedKey: apiKey.substring(0, 8) + '...'
    });
    
    return res.status(401).json({
      error: 'Invalid API key',
      message: 'The provided API key is not valid'
    });
  }
  
  req.isApiRequest = true;
  next();
};

module.exports = {
  authenticate,
  optionalAuth,
  authorize,
  requirePermission,
  requireOwnership,
  authenticateApiKey,
  generateToken,
  verifyToken
};
