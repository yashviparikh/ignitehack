/**
 * Express.js Server Entry Point
 * =============================
 * 
 * Main server file for the Express.js hackathon template.
 * This file initializes and starts the Express application.
 */

const app = require('./src/app');
const config = require('./src/config/database');
const logger = require('./src/utils/logger');

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

/**
 * Start the server
 */
async function startServer() {
    try {
        // Initialize database connections if needed
        logger.info('🚀 Starting Express.js Cloud Template Server...');
        
        // Start the server
        const server = app.listen(PORT, HOST, () => {
            logger.info(`✅ Server running on http://${HOST}:${PORT}`);
            logger.info(`📚 API Documentation: http://${HOST}:${PORT}/api-docs`);
            logger.info(`🏥 Health Check: http://${HOST}:${PORT}/health`);
            logger.info(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
        });

        // Graceful shutdown handling
        process.on('SIGTERM', () => {
            logger.info('🛑 SIGTERM received, shutting down gracefully...');
            server.close(() => {
                logger.info('✅ Server closed');
                process.exit(0);
            });
        });

        process.on('SIGINT', () => {
            logger.info('🛑 SIGINT received, shutting down gracefully...');
            server.close(() => {
                logger.info('✅ Server closed');
                process.exit(0);
            });
        });

        return server;
    } catch (error) {
        logger.error('❌ Failed to start server:', error);
        process.exit(1);
    }
}

// Start the server if this file is run directly
if (require.main === module) {
    startServer();
}

module.exports = { startServer };
