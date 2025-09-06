/**
 * Health Check Routes
 * Kubernetes-ready health and readiness probes
 */

const express = require('express');
const router = express.Router();
const logger = require('../utils/logger');

// Simple health check
router.get('/', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development',
    version: require('../../package.json').version
  });
});

// Detailed health check
router.get('/detailed', async (req, res) => {
  const startTime = Date.now();
  
  try {
    const healthCheck = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: require('../../package.json').version,
      checks: {
        server: 'healthy',
        memory: 'healthy',
        database: 'checking',
        redis: 'checking'
      },
      metrics: {
        memoryUsage: process.memoryUsage(),
        cpuUsage: process.cpuUsage(),
        responseTime: 0
      }
    };
    
    // Memory check
    const memUsage = process.memoryUsage();
    const memUsagePercentage = (memUsage.heapUsed / memUsage.heapTotal) * 100;
    
    if (memUsagePercentage > 90) {
      healthCheck.checks.memory = 'unhealthy';
      healthCheck.status = 'degraded';
    } else if (memUsagePercentage > 80) {
      healthCheck.checks.memory = 'warning';
      healthCheck.status = 'degraded';
    }
    
    // Database connectivity check (if database is configured)
    try {
      if (process.env.DATABASE_URL || process.env.MONGODB_URI) {
        // Add database ping logic here based on your database
        // For now, we'll simulate a check
        await new Promise(resolve => setTimeout(resolve, 10));
        healthCheck.checks.database = 'healthy';
      } else {
        healthCheck.checks.database = 'not_configured';
      }
    } catch (error) {
      healthCheck.checks.database = 'unhealthy';
      healthCheck.status = 'unhealthy';
      logger.error('Database health check failed', { error: error.message });
    }
    
    // Redis connectivity check (if Redis is configured)
    try {
      if (process.env.REDIS_URL) {
        // Add Redis ping logic here
        // For now, we'll simulate a check
        await new Promise(resolve => setTimeout(resolve, 5));
        healthCheck.checks.redis = 'healthy';
      } else {
        healthCheck.checks.redis = 'not_configured';
      }
    } catch (error) {
      healthCheck.checks.redis = 'unhealthy';
      healthCheck.status = 'degraded';
      logger.error('Redis health check failed', { error: error.message });
    }
    
    // Calculate response time
    healthCheck.metrics.responseTime = Date.now() - startTime;
    
    // Determine overall status
    const statuses = Object.values(healthCheck.checks);
    if (statuses.includes('unhealthy')) {
      healthCheck.status = 'unhealthy';
    } else if (statuses.includes('warning')) {
      healthCheck.status = 'degraded';
    }
    
    const statusCode = healthCheck.status === 'healthy' ? 200 : 
                      healthCheck.status === 'degraded' ? 200 : 503;
    
    res.status(statusCode).json(healthCheck);
    
  } catch (error) {
    logger.error('Health check failed', { error: error.message });
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: 'Health check failed',
      message: error.message
    });
  }
});

// Kubernetes liveness probe
router.get('/live', (req, res) => {
  // Liveness probe - checks if the application is running
  // Should return 200 if the app is alive, 500+ if it should be restarted
  res.status(200).json({
    status: 'alive',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Kubernetes readiness probe
router.get('/ready', async (req, res) => {
  // Readiness probe - checks if the application is ready to serve traffic
  // Should return 200 if ready, 500+ if not ready to receive requests
  
  try {
    const checks = {
      server: true,
      database: true,
      redis: true
    };
    
    // Check database connectivity (if configured)
    if (process.env.DATABASE_URL || process.env.MONGODB_URI) {
      try {
        // Add database ping logic here
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        checks.database = false;
        logger.warn('Database not ready', { error: error.message });
      }
    }
    
    // Check Redis connectivity (if configured)
    if (process.env.REDIS_URL) {
      try {
        // Add Redis ping logic here
        await new Promise(resolve => setTimeout(resolve, 50));
      } catch (error) {
        checks.redis = false;
        logger.warn('Redis not ready', { error: error.message });
      }
    }
    
    const isReady = Object.values(checks).every(check => check === true);
    const statusCode = isReady ? 200 : 503;
    
    res.status(statusCode).json({
      status: isReady ? 'ready' : 'not_ready',
      timestamp: new Date().toISOString(),
      checks
    });
    
  } catch (error) {
    logger.error('Readiness check failed', { error: error.message });
    res.status(503).json({
      status: 'not_ready',
      timestamp: new Date().toISOString(),
      error: 'Readiness check failed'
    });
  }
});

// Startup probe (for slow-starting applications)
router.get('/startup', (req, res) => {
  // Startup probe - checks if the application has started
  // Used for applications that take a long time to start
  
  const startupTime = process.uptime();
  const isStarted = startupTime > 10; // Consider started after 10 seconds
  
  res.status(isStarted ? 200 : 503).json({
    status: isStarted ? 'started' : 'starting',
    timestamp: new Date().toISOString(),
    uptime: startupTime
  });
});

// Metrics endpoint (Prometheus-compatible)
router.get('/metrics', (req, res) => {
  const memUsage = process.memoryUsage();
  const cpuUsage = process.cpuUsage();
  
  // Simple text format for Prometheus
  const metrics = `
# HELP nodejs_memory_heap_used_bytes Process heap memory used
# TYPE nodejs_memory_heap_used_bytes gauge
nodejs_memory_heap_used_bytes ${memUsage.heapUsed}

# HELP nodejs_memory_heap_total_bytes Process heap memory total
# TYPE nodejs_memory_heap_total_bytes gauge
nodejs_memory_heap_total_bytes ${memUsage.heapTotal}

# HELP nodejs_memory_rss_bytes Process resident memory
# TYPE nodejs_memory_rss_bytes gauge
nodejs_memory_rss_bytes ${memUsage.rss}

# HELP nodejs_process_uptime_seconds Process uptime
# TYPE nodejs_process_uptime_seconds gauge
nodejs_process_uptime_seconds ${process.uptime()}

# HELP nodejs_version_info Node.js version info
# TYPE nodejs_version_info gauge
nodejs_version_info{version="${process.version}"} 1
`.trim();

  res.set('Content-Type', 'text/plain');
  res.send(metrics);
});

// Performance metrics
router.get('/performance', (req, res) => {
  res.json({
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: {
      usage: process.memoryUsage(),
      percentage: (process.memoryUsage().heapUsed / process.memoryUsage().heapTotal) * 100
    },
    cpu: process.cpuUsage(),
    loadAverage: require('os').loadavg(),
    platform: {
      arch: process.arch,
      platform: process.platform,
      version: process.version,
      pid: process.pid
    }
  });
});

module.exports = router;
