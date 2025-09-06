/**
 * Global Error Handler Middleware
 * Centralized error handling with logging and sanitized responses
 */

const logger = require('../utils/logger');

/**
 * Custom error class for application errors
 */
class AppError extends Error {
  constructor(message, statusCode = 500, isOperational = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.timestamp = new Date().toISOString();
    
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Validation error handler
 */
const handleValidationError = (error) => {
  const errors = Object.values(error.errors).map(err => ({
    field: err.path,
    message: err.message,
    value: err.value
  }));
  
  return new AppError(`Validation failed: ${errors.map(e => e.message).join(', ')}`, 400);
};

/**
 * JWT error handler
 */
const handleJWTError = (error) => {
  if (error.name === 'JsonWebTokenError') {
    return new AppError('Invalid token', 401);
  }
  if (error.name === 'TokenExpiredError') {
    return new AppError('Token expired', 401);
  }
  return new AppError('Authentication failed', 401);
};

/**
 * MongoDB duplicate key error handler
 */
const handleDuplicateKeyError = (error) => {
  const field = Object.keys(error.keyValue)[0];
  const value = error.keyValue[field];
  return new AppError(`${field} '${value}' already exists`, 409);
};

/**
 * MongoDB cast error handler
 */
const handleCastError = (error) => {
  return new AppError(`Invalid ${error.path}: ${error.value}`, 400);
};

/**
 * Rate limit error handler
 */
const handleRateLimitError = () => {
  return new AppError('Too many requests, please try again later', 429);
};

/**
 * File upload error handler
 */
const handleMulterError = (error) => {
  if (error.code === 'LIMIT_FILE_SIZE') {
    return new AppError('File too large', 413);
  }
  if (error.code === 'LIMIT_FILE_COUNT') {
    return new AppError('Too many files', 413);
  }
  if (error.code === 'LIMIT_UNEXPECTED_FILE') {
    return new AppError('Unexpected file field', 400);
  }
  return new AppError('File upload error', 400);
};

/**
 * Development error response
 */
const sendErrorDev = (err, req, res) => {
  // Log error with full details
  logger.error('Development Error', {
    requestId: req.requestId,
    error: {
      name: err.name,
      message: err.message,
      stack: err.stack,
      statusCode: err.statusCode
    },
    request: {
      method: req.method,
      url: req.originalUrl,
      ip: req.ip,
      userAgent: req.get('User-Agent')
    }
  });
  
  res.status(err.statusCode || 500).json({
    success: false,
    error: {
      name: err.name,
      message: err.message,
      statusCode: err.statusCode,
      stack: err.stack,
      timestamp: err.timestamp || new Date().toISOString()
    },
    request: {
      id: req.requestId,
      method: req.method,
      url: req.originalUrl
    }
  });
};

/**
 * Production error response
 */
const sendErrorProd = (err, req, res) => {
  // Log error for monitoring
  logger.error('Production Error', {
    requestId: req.requestId,
    error: {
      name: err.name,
      message: err.isOperational ? err.message : 'Internal server error',
      statusCode: err.statusCode,
      stack: err.stack
    },
    request: {
      method: req.method,
      url: req.originalUrl,
      ip: req.ip,
      userId: req.user?.id
    }
  });
  
  // Send sanitized error to client
  if (err.isOperational) {
    res.status(err.statusCode).json({
      success: false,
      error: {
        message: err.message,
        statusCode: err.statusCode,
        timestamp: err.timestamp || new Date().toISOString()
      },
      requestId: req.requestId
    });
  } else {
    // Don't leak error details in production
    res.status(500).json({
      success: false,
      error: {
        message: 'Something went wrong!',
        statusCode: 500,
        timestamp: new Date().toISOString()
      },
      requestId: req.requestId
    });
  }
};

/**
 * Main error handler middleware
 */
const errorHandler = (err, req, res, next) => {
  let error = { ...err };
  error.message = err.message;
  error.statusCode = err.statusCode;
  
  // Handle specific error types
  if (err.name === 'ValidationError') {
    error = handleValidationError(err);
  }
  
  if (err.name === 'JsonWebTokenError' || err.name === 'TokenExpiredError') {
    error = handleJWTError(err);
  }
  
  if (err.code === 11000) {
    error = handleDuplicateKeyError(err);
  }
  
  if (err.name === 'CastError') {
    error = handleCastError(err);
  }
  
  if (err.type === 'entity.too.large') {
    error = new AppError('Request entity too large', 413);
  }
  
  if (err.code === 'LIMIT_FILE_SIZE' || err.code === 'LIMIT_FILE_COUNT' || err.code === 'LIMIT_UNEXPECTED_FILE') {
    error = handleMulterError(err);
  }
  
  if (err.type === 'RateLimiterError') {
    error = handleRateLimitError();
  }
  
  // Handle CORS errors
  if (err.message && err.message.includes('CORS')) {
    error = new AppError('CORS policy violation', 403);
  }
  
  // Send error response
  if (process.env.NODE_ENV === 'development') {
    sendErrorDev(error, req, res);
  } else {
    sendErrorProd(error, req, res);
  }
};

/**
 * Async error catcher wrapper
 */
const catchAsync = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

/**
 * 404 handler for undefined routes
 */
const notFound = (req, res, next) => {
  const error = new AppError(`Route ${req.originalUrl} not found`, 404);
  next(error);
};

module.exports = {
  errorHandler,
  AppError,
  catchAsync,
  notFound
};
