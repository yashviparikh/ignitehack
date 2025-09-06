/**
 * Swagger/OpenAPI Configuration
 * Automatic API documentation generation
 */

const swaggerJsdoc = require('swagger-jsdoc');
const packageJson = require('../../package.json');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Hackathon Express Security API',
      version: packageJson.version,
      description: `
        Production-ready Express.js API template with built-in security and cloud-native features.
        
        ## Features
        - 🔐 JWT Authentication with role-based access control
        - 🛡️ Comprehensive security middleware (Helmet, rate limiting, input validation)
        - 📊 Health checks and monitoring endpoints
        - 🚀 Cloud-native ready (Docker, Kubernetes)
        - 📝 Project and task management examples
        - 🔍 Audit logging for compliance
        
        ## Security
        - All endpoints require authentication unless marked as public
        - Rate limiting applied to prevent abuse
        - Input validation and sanitization
        - CORS protection
        - Helmet security headers
        
        ## Authentication
        1. Register a new account at \`/api/auth/register\`
        2. Login to get JWT token at \`/api/auth/login\`
        3. Include token in Authorization header: \`Bearer YOUR_TOKEN\`
      `,
      contact: {
        name: 'Hackathon Templates',
        url: 'https://github.com/hackathon-templates',
        email: 'support@hackathon-templates.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: process.env.API_BASE_URL || 'http://localhost:3000',
        description: 'Development server'
      },
      {
        url: 'https://api.hackathon-template.com',
        description: 'Production server'
      }
    ],
    components: {
      securitySchemes: {
        BearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
          description: 'JWT token obtained from /api/auth/login'
        },
        ApiKeyAuth: {
          type: 'apiKey',
          in: 'header',
          name: 'X-API-Key',
          description: 'API key for service-to-service communication'
        }
      },
      schemas: {
        User: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Unique user identifier',
              example: 'user_1701234567890_abc123'
            },
            email: {
              type: 'string',
              format: 'email',
              description: 'User email address',
              example: 'john.doe@example.com'
            },
            name: {
              type: 'string',
              description: 'User full name',
              example: 'John Doe'
            },
            role: {
              type: 'string',
              enum: ['user', 'admin', 'moderator'],
              description: 'User role',
              example: 'user'
            },
            permissions: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'User permissions',
              example: ['read', 'write']
            },
            isActive: {
              type: 'boolean',
              description: 'Whether user account is active',
              example: true
            },
            createdAt: {
              type: 'string',
              format: 'date-time',
              description: 'Account creation timestamp',
              example: '2023-11-29T10:30:00.000Z'
            },
            lastLogin: {
              type: 'string',
              format: 'date-time',
              description: 'Last login timestamp',
              example: '2023-11-29T15:45:00.000Z'
            }
          }
        },
        Project: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Unique project identifier',
              example: 'project_1701234567890_xyz789'
            },
            name: {
              type: 'string',
              description: 'Project name',
              example: 'Awesome Hackathon Project'
            },
            description: {
              type: 'string',
              description: 'Project description',
              example: 'An innovative solution for modern problems'
            },
            category: {
              type: 'string',
              enum: ['web', 'mobile', 'ai', 'blockchain', 'iot', 'fintech', 'healthtech', 'edutech'],
              description: 'Project category',
              example: 'web'
            },
            tags: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Project tags',
              example: ['react', 'nodejs', 'mongodb']
            },
            status: {
              type: 'string',
              enum: ['active', 'completed', 'archived'],
              description: 'Project status',
              example: 'active'
            },
            createdBy: {
              type: 'string',
              description: 'User ID who created the project',
              example: 'user_1701234567890_abc123'
            },
            team: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Team member user IDs',
              example: ['user_1701234567890_abc123', 'user_1701234567890_def456']
            },
            createdAt: {
              type: 'string',
              format: 'date-time',
              description: 'Project creation timestamp',
              example: '2023-11-29T10:30:00.000Z'
            },
            updatedAt: {
              type: 'string',
              format: 'date-time',
              description: 'Project last update timestamp',
              example: '2023-11-29T15:45:00.000Z'
            }
          }
        },
        Task: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Unique task identifier',
              example: 'task_1701234567890_uvw456'
            },
            title: {
              type: 'string',
              description: 'Task title',
              example: 'Implement user authentication'
            },
            description: {
              type: 'string',
              description: 'Task description',
              example: 'Add JWT-based authentication with role management'
            },
            priority: {
              type: 'string',
              enum: ['low', 'medium', 'high', 'critical'],
              description: 'Task priority level',
              example: 'high'
            },
            status: {
              type: 'string',
              enum: ['todo', 'in_progress', 'review', 'done'],
              description: 'Task status',
              example: 'in_progress'
            },
            projectId: {
              type: 'string',
              description: 'Associated project ID',
              example: 'project_1701234567890_xyz789'
            },
            assignedTo: {
              type: 'string',
              description: 'User ID assigned to this task',
              example: 'user_1701234567890_abc123'
            },
            createdBy: {
              type: 'string',
              description: 'User ID who created the task',
              example: 'user_1701234567890_abc123'
            },
            dueDate: {
              type: 'string',
              format: 'date-time',
              description: 'Task due date',
              example: '2023-12-01T23:59:59.000Z'
            },
            createdAt: {
              type: 'string',
              format: 'date-time',
              description: 'Task creation timestamp',
              example: '2023-11-29T10:30:00.000Z'
            },
            updatedAt: {
              type: 'string',
              format: 'date-time',
              description: 'Task last update timestamp',
              example: '2023-11-29T15:45:00.000Z'
            }
          }
        },
        Error: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: false
            },
            error: {
              type: 'string',
              description: 'Error type',
              example: 'Validation failed'
            },
            message: {
              type: 'string',
              description: 'Human-readable error message',
              example: 'The provided data is invalid'
            },
            details: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  field: {
                    type: 'string',
                    example: 'email'
                  },
                  message: {
                    type: 'string',
                    example: 'Email is required'
                  }
                }
              },
              description: 'Detailed validation errors'
            },
            requestId: {
              type: 'string',
              description: 'Request ID for tracking',
              example: '550e8400-e29b-41d4-a716-446655440000'
            }
          }
        },
        SuccessResponse: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: true
            },
            message: {
              type: 'string',
              description: 'Success message',
              example: 'Operation completed successfully'
            },
            data: {
              type: 'object',
              description: 'Response data'
            }
          }
        },
        PaginationMeta: {
          type: 'object',
          properties: {
            currentPage: {
              type: 'integer',
              description: 'Current page number',
              example: 1
            },
            totalPages: {
              type: 'integer',
              description: 'Total number of pages',
              example: 5
            },
            totalItems: {
              type: 'integer',
              description: 'Total number of items',
              example: 42
            },
            hasNextPage: {
              type: 'boolean',
              description: 'Whether there is a next page',
              example: true
            },
            hasPrevPage: {
              type: 'boolean',
              description: 'Whether there is a previous page',
              example: false
            },
            limit: {
              type: 'integer',
              description: 'Items per page',
              example: 10
            }
          }
        },
        HealthCheck: {
          type: 'object',
          properties: {
            status: {
              type: 'string',
              enum: ['healthy', 'degraded', 'unhealthy'],
              description: 'Overall health status',
              example: 'healthy'
            },
            timestamp: {
              type: 'string',
              format: 'date-time',
              description: 'Health check timestamp',
              example: '2023-11-29T15:45:00.000Z'
            },
            uptime: {
              type: 'number',
              description: 'Application uptime in seconds',
              example: 3600
            },
            environment: {
              type: 'string',
              description: 'Current environment',
              example: 'development'
            },
            version: {
              type: 'string',
              description: 'Application version',
              example: '1.0.0'
            }
          }
        }
      },
      responses: {
        UnauthorizedError: {
          description: 'Authentication failed',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                success: false,
                error: 'Authentication failed',
                message: 'Invalid or expired token'
              }
            }
          }
        },
        ForbiddenError: {
          description: 'Insufficient permissions',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                success: false,
                error: 'Insufficient permissions',
                message: 'You do not have permission to access this resource'
              }
            }
          }
        },
        NotFoundError: {
          description: 'Resource not found',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                success: false,
                error: 'Resource not found',
                message: 'The requested resource could not be found'
              }
            }
          }
        },
        ValidationError: {
          description: 'Validation failed',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                success: false,
                error: 'Validation failed',
                message: 'The provided data is invalid',
                details: [
                  {
                    field: 'email',
                    message: 'Email is required'
                  },
                  {
                    field: 'password',
                    message: 'Password must be at least 8 characters'
                  }
                ]
              }
            }
          }
        },
        RateLimitError: {
          description: 'Rate limit exceeded',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              },
              example: {
                success: false,
                error: 'Too many requests',
                message: 'Rate limit exceeded. Please try again later.'
              }
            }
          }
        }
      }
    },
    security: [
      {
        BearerAuth: []
      }
    ],
    tags: [
      {
        name: 'Authentication',
        description: 'User authentication and authorization endpoints'
      },
      {
        name: 'Users',
        description: 'User management operations'
      },
      {
        name: 'Projects',
        description: 'Project management operations'
      },
      {
        name: 'Tasks',
        description: 'Task management operations'
      },
      {
        name: 'Health',
        description: 'Health check and monitoring endpoints'
      }
    ]
  },
  apis: [
    './src/routes/*.js', // Include all route files
    './src/server.js'    // Include main server file
  ]
};

const specs = swaggerJsdoc(options);

module.exports = specs;
