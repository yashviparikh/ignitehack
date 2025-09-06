/**
 * Database Configuration
 * Multi-database support with connection pooling and monitoring
 */

const logger = require('../utils/logger');

// Database configuration object
const dbConfig = {
  // MongoDB Configuration
  mongodb: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/hackathon_db',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      maxPoolSize: 10, // Maximum number of connections
      serverSelectionTimeoutMS: 5000, // Keep trying to send operations for 5 seconds
      socketTimeoutMS: 45000, // Close sockets after 45 seconds of inactivity
      family: 4, // Use IPv4, skip trying IPv6
      bufferMaxEntries: 0,
      bufferCommands: false,
    }
  },
  
  // PostgreSQL Configuration
  postgresql: {
    host: process.env.PG_HOST || 'localhost',
    port: process.env.PG_PORT || 5432,
    database: process.env.PG_DATABASE || 'hackathon_db',
    username: process.env.PG_USERNAME || 'postgres',
    password: process.env.PG_PASSWORD || 'password',
    dialect: 'postgres',
    pool: {
      max: 10,
      min: 0,
      acquire: 30000,
      idle: 10000
    },
    logging: (msg) => logger.debug('PostgreSQL:', msg),
    dialectOptions: {
      ssl: process.env.NODE_ENV === 'production' ? {
        require: true,
        rejectUnauthorized: false
      } : false
    }
  },
  
  // Redis Configuration
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD || undefined,
    db: process.env.REDIS_DB || 0,
    retryDelayOnFailover: 100,
    enableReadyCheck: true,
    maxRetriesPerRequest: 3,
    lazyConnect: true,
    connectTimeout: 10000,
    commandTimeout: 5000,
    family: 4
  }
};

// Database connection status
const connectionStatus = {
  mongodb: 'disconnected',
  postgresql: 'disconnected',
  redis: 'disconnected'
};

/**
 * MongoDB Connection Setup
 */
const connectMongoDB = async () => {
  if (!process.env.MONGODB_URI && !process.env.ENABLE_MONGODB) {
    logger.info('MongoDB not configured, skipping connection');
    return null;
  }
  
  try {
    const mongoose = require('mongoose');
    
    // Connection event handlers
    mongoose.connection.on('connected', () => {
      connectionStatus.mongodb = 'connected';
      logger.info('MongoDB connected successfully');
    });
    
    mongoose.connection.on('error', (err) => {
      connectionStatus.mongodb = 'error';
      logger.error('MongoDB connection error:', err);
    });
    
    mongoose.connection.on('disconnected', () => {
      connectionStatus.mongodb = 'disconnected';
      logger.warn('MongoDB disconnected');
    });
    
    // Graceful close on app termination
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      logger.info('MongoDB connection closed through app termination');
    });
    
    await mongoose.connect(dbConfig.mongodb.uri, dbConfig.mongodb.options);
    return mongoose;
    
  } catch (error) {
    connectionStatus.mongodb = 'error';
    logger.error('Failed to connect to MongoDB:', error);
    return null;
  }
};

/**
 * PostgreSQL Connection Setup
 */
const connectPostgreSQL = async () => {
  if (!process.env.PG_HOST && !process.env.ENABLE_POSTGRESQL) {
    logger.info('PostgreSQL not configured, skipping connection');
    return null;
  }
  
  try {
    const { Sequelize } = require('sequelize');
    
    const sequelize = new Sequelize(
      dbConfig.postgresql.database,
      dbConfig.postgresql.username,
      dbConfig.postgresql.password,
      {
        host: dbConfig.postgresql.host,
        port: dbConfig.postgresql.port,
        dialect: dbConfig.postgresql.dialect,
        pool: dbConfig.postgresql.pool,
        logging: dbConfig.postgresql.logging,
        dialectOptions: dbConfig.postgresql.dialectOptions
      }
    );
    
    // Test the connection
    await sequelize.authenticate();
    connectionStatus.postgresql = 'connected';
    logger.info('PostgreSQL connected successfully');
    
    // Sync models (in development)
    if (process.env.NODE_ENV === 'development') {
      await sequelize.sync({ alter: true });
      logger.info('PostgreSQL models synchronized');
    }
    
    return sequelize;
    
  } catch (error) {
    connectionStatus.postgresql = 'error';
    logger.error('Failed to connect to PostgreSQL:', error);
    return null;
  }
};

/**
 * Redis Connection Setup
 */
const connectRedis = async () => {
  if (!process.env.REDIS_HOST && !process.env.ENABLE_REDIS) {
    logger.info('Redis not configured, skipping connection');
    return null;
  }
  
  try {
    const Redis = require('ioredis');
    
    const redis = new Redis(dbConfig.redis);
    
    redis.on('connect', () => {
      connectionStatus.redis = 'connected';
      logger.info('Redis connected successfully');
    });
    
    redis.on('error', (err) => {
      connectionStatus.redis = 'error';
      logger.error('Redis connection error:', err);
    });
    
    redis.on('close', () => {
      connectionStatus.redis = 'disconnected';
      logger.warn('Redis connection closed');
    });
    
    // Test connection
    await redis.ping();
    
    return redis;
    
  } catch (error) {
    connectionStatus.redis = 'error';
    logger.error('Failed to connect to Redis:', error);
    return null;
  }
};

/**
 * Initialize all database connections
 */
const initializeDatabases = async () => {
  logger.info('Initializing database connections...');
  
  const connections = {
    mongodb: null,
    postgresql: null,
    redis: null
  };
  
  // Connect to databases in parallel
  const [mongodb, postgresql, redis] = await Promise.allSettled([
    connectMongoDB(),
    connectPostgreSQL(),
    connectRedis()
  ]);
  
  // Handle MongoDB connection
  if (mongodb.status === 'fulfilled' && mongodb.value) {
    connections.mongodb = mongodb.value;
  }
  
  // Handle PostgreSQL connection
  if (postgresql.status === 'fulfilled' && postgresql.value) {
    connections.postgresql = postgresql.value;
  }
  
  // Handle Redis connection
  if (redis.status === 'fulfilled' && redis.value) {
    connections.redis = redis.value;
  }
  
  // Log connection summary
  const connectedDatabases = Object.entries(connectionStatus)
    .filter(([_, status]) => status === 'connected')
    .map(([db, _]) => db);
  
  if (connectedDatabases.length > 0) {
    logger.info(`Successfully connected to: ${connectedDatabases.join(', ')}`);
  } else {
    logger.warn('No databases connected - running in standalone mode');
  }
  
  return connections;
};

/**
 * Health check for all databases
 */
const checkDatabaseHealth = async (connections) => {
  const health = {
    mongodb: { status: 'not_configured', latency: null, error: null },
    postgresql: { status: 'not_configured', latency: null, error: null },
    redis: { status: 'not_configured', latency: null, error: null }
  };
  
  // Check MongoDB
  if (connections.mongodb) {
    try {
      const start = Date.now();
      await connections.mongodb.connection.db.admin().ping();
      health.mongodb = {
        status: 'healthy',
        latency: Date.now() - start,
        error: null
      };
    } catch (error) {
      health.mongodb = {
        status: 'unhealthy',
        latency: null,
        error: error.message
      };
    }
  }
  
  // Check PostgreSQL
  if (connections.postgresql) {
    try {
      const start = Date.now();
      await connections.postgresql.authenticate();
      health.postgresql = {
        status: 'healthy',
        latency: Date.now() - start,
        error: null
      };
    } catch (error) {
      health.postgresql = {
        status: 'unhealthy',
        latency: null,
        error: error.message
      };
    }
  }
  
  // Check Redis
  if (connections.redis) {
    try {
      const start = Date.now();
      await connections.redis.ping();
      health.redis = {
        status: 'healthy',
        latency: Date.now() - start,
        error: null
      };
    } catch (error) {
      health.redis = {
        status: 'unhealthy',
        latency: null,
        error: error.message
      };
    }
  }
  
  return health;
};

/**
 * Close all database connections gracefully
 */
const closeDatabaseConnections = async (connections) => {
  logger.info('Closing database connections...');
  
  const closePromises = [];
  
  if (connections.mongodb) {
    closePromises.push(
      connections.mongodb.connection.close()
        .then(() => logger.info('MongoDB connection closed'))
        .catch(err => logger.error('Error closing MongoDB:', err))
    );
  }
  
  if (connections.postgresql) {
    closePromises.push(
      connections.postgresql.close()
        .then(() => logger.info('PostgreSQL connection closed'))
        .catch(err => logger.error('Error closing PostgreSQL:', err))
    );
  }
  
  if (connections.redis) {
    closePromises.push(
      connections.redis.quit()
        .then(() => logger.info('Redis connection closed'))
        .catch(err => logger.error('Error closing Redis:', err))
    );
  }
  
  await Promise.allSettled(closePromises);
  logger.info('All database connections closed');
};

module.exports = {
  dbConfig,
  connectionStatus,
  initializeDatabases,
  checkDatabaseHealth,
  closeDatabaseConnections,
  connectMongoDB,
  connectPostgreSQL,
  connectRedis
};
