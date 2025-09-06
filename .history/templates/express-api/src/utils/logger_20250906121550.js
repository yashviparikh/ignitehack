/**
 * Winston Logger Configuration
 * Structured logging with different levels and formats
 */

const winston = require('winston');
const path = require('path');

// Define log levels
const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4
};

// Define colors for each level
const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'white'
};

// Tell winston that you want to link the colors
winston.addColors(colors);

// Define format for logs
const format = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.prettyPrint()
);

// Define format for console logs (development)
const consoleFormat = winston.format.combine(
  winston.format.timestamp({ format: 'HH:mm:ss' }),
  winston.format.colorize({ all: true }),
  winston.format.printf(
    (info) => {
      const { timestamp, level, message, ...meta } = info;
      const metaStr = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
      return `${timestamp} [${level}]: ${message} ${metaStr}`;
    }
  )
);

// Define which transports the logger must use
const transports = [];

// Console transport (always enabled in development)
if (process.env.NODE_ENV !== 'production') {
  transports.push(
    new winston.transports.Console({
      level: 'debug',
      format: consoleFormat
    })
  );
} else {
  transports.push(
    new winston.transports.Console({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      )
    })
  );
}

// File transports for production
if (process.env.NODE_ENV === 'production') {
  // Error log file
  transports.push(
    new winston.transports.File({
      filename: path.join(process.cwd(), 'logs', 'error.log'),
      level: 'error',
      format,
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  );
  
  // Combined log file
  transports.push(
    new winston.transports.File({
      filename: path.join(process.cwd(), 'logs', 'combined.log'),
      format,
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  );
  
  // HTTP log file
  transports.push(
    new winston.transports.File({
      filename: path.join(process.cwd(), 'logs', 'http.log'),
      level: 'http',
      format,
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  );
}

// Create the logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || (process.env.NODE_ENV === 'production' ? 'info' : 'debug'),
  levels,
  format,
  transports,
  exitOnError: false,
  silent: process.env.NODE_ENV === 'test'
});

// Create logs directory if it doesn't exist
const fs = require('fs');
const logsDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Add request logging helper
logger.logRequest = (req, res, responseTime) => {
  logger.http('HTTP Request', {
    requestId: req.requestId,
    method: req.method,
    url: req.originalUrl,
    ip: req.ip || req.connection.remoteAddress,
    userAgent: req.get('User-Agent'),
    statusCode: res.statusCode,
    responseTime: `${responseTime}ms`,
    contentLength: res.get('Content-Length'),
    userId: req.user?.id,
    timestamp: new Date().toISOString()
  });
};

// Add security logging helper
logger.logSecurity = (event, details, req) => {
  logger.warn('Security Event', {
    event,
    requestId: req?.requestId,
    ip: req?.ip,
    userAgent: req?.get('User-Agent'),
    userId: req?.user?.id,
    timestamp: new Date().toISOString(),
    details
  });
};

// Add performance logging helper
logger.logPerformance = (operation, duration, metadata = {}) => {
  logger.info('Performance Metric', {
    operation,
    duration: `${duration}ms`,
    timestamp: new Date().toISOString(),
    ...metadata
  });
};

// Add database operation logging helper
logger.logDatabase = (operation, collection, query, duration) => {
  logger.debug('Database Operation', {
    operation,
    collection,
    query: JSON.stringify(query),
    duration: `${duration}ms`,
    timestamp: new Date().toISOString()
  });
};

// Add audit logging helper for compliance
logger.audit = (action, resource, userId, metadata = {}) => {
  logger.info('Audit Log', {
    action,
    resource,
    userId,
    timestamp: new Date().toISOString(),
    ...metadata
  });
};

module.exports = logger;
