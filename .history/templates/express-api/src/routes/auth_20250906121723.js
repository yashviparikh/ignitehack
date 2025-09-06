/**
 * Authentication Routes
 * JWT-based authentication with registration, login, and security features
 */

const express = require('express');
const bcrypt = require('bcryptjs');
const { body, validationResult } = require('express-validator');
const rateLimit = require('express-rate-limit');
const router = express.Router();

const { generateToken, authenticate } = require('../middleware/auth');
const { catchAsync, AppError } = require('../middleware/errorHandler');
const logger = require('../utils/logger');

// Rate limiting for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per windowMs
  message: {
    error: 'Too many authentication attempts, please try again later',
    retryAfter: 15 * 60 * 1000
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Stricter rate limiting for password reset
const passwordResetLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 3, // Only 3 password reset attempts per hour
  message: {
    error: 'Too many password reset attempts, please try again later',
    retryAfter: 60 * 60 * 1000
  }
});

// Validation rules
const registerValidation = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character'),
  body('name')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Name must be between 2 and 50 characters'),
  body('role')
    .optional()
    .isIn(['user', 'admin', 'moderator'])
    .withMessage('Invalid role specified')
];

const loginValidation = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

const changePasswordValidation = [
  body('currentPassword')
    .notEmpty()
    .withMessage('Current password is required'),
  body('newPassword')
    .isLength({ min: 8 })
    .withMessage('New password must be at least 8 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('New password must contain at least one lowercase letter, one uppercase letter, one number, and one special character')
];

// In-memory user store (replace with database in production)
const users = new Map();

// Helper function to find user by email
const findUserByEmail = (email) => {
  for (const [id, user] of users) {
    if (user.email === email) {
      return { id, ...user };
    }
  }
  return null;
};

// Helper function to find user by ID
const findUserById = (id) => {
  const user = users.get(id);
  return user ? { id, ...user } : null;
};

/**
 * @route   POST /api/auth/register
 * @desc    Register a new user
 * @access  Public
 */
router.post('/register', authLimiter, registerValidation, catchAsync(async (req, res) => {
  // Check validation results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array()
    });
  }
  
  const { email, password, name, role = 'user' } = req.body;
  
  // Check if user already exists
  const existingUser = findUserByEmail(email);
  if (existingUser) {
    logger.logSecurity('Registration attempt with existing email', { email }, req);
    return res.status(409).json({
      success: false,
      error: 'User already exists',
      message: 'A user with this email already exists'
    });
  }
  
  // Hash password
  const saltRounds = 12;
  const hashedPassword = await bcrypt.hash(password, saltRounds);
  
  // Create user
  const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const newUser = {
    email,
    password: hashedPassword,
    name,
    role,
    permissions: role === 'admin' ? ['read', 'write', 'delete', 'admin'] : ['read', 'write'],
    createdAt: new Date().toISOString(),
    lastLogin: null,
    isActive: true,
    loginAttempts: 0,
    lockedUntil: null
  };
  
  users.set(userId, newUser);
  
  // Generate token
  const token = generateToken({
    userId,
    email,
    role,
    permissions: newUser.permissions
  });
  
  // Log successful registration
  logger.audit('user_registered', 'user', userId, {
    email,
    role,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  
  res.status(201).json({
    success: true,
    message: 'User registered successfully',
    data: {
      user: {
        id: userId,
        email,
        name,
        role,
        permissions: newUser.permissions,
        createdAt: newUser.createdAt
      },
      token
    }
  });
}));

/**
 * @route   POST /api/auth/login
 * @desc    Login user
 * @access  Public
 */
router.post('/login', authLimiter, loginValidation, catchAsync(async (req, res) => {
  // Check validation results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array()
    });
  }
  
  const { email, password } = req.body;
  
  // Find user
  const user = findUserByEmail(email);
  if (!user) {
    logger.logSecurity('Login attempt with non-existent email', { email }, req);
    return res.status(401).json({
      success: false,
      error: 'Invalid credentials',
      message: 'Email or password is incorrect'
    });
  }
  
  // Check if account is locked
  if (user.lockedUntil && new Date() < new Date(user.lockedUntil)) {
    logger.logSecurity('Login attempt on locked account', { email, userId: user.id }, req);
    return res.status(423).json({
      success: false,
      error: 'Account locked',
      message: 'Account is temporarily locked due to too many failed login attempts'
    });
  }
  
  // Check if account is active
  if (!user.isActive) {
    logger.logSecurity('Login attempt on inactive account', { email, userId: user.id }, req);
    return res.status(401).json({
      success: false,
      error: 'Account inactive',
      message: 'Your account has been deactivated'
    });
  }
  
  // Verify password
  const isPasswordValid = await bcrypt.compare(password, user.password);
  if (!isPasswordValid) {
    // Increment login attempts
    user.loginAttempts = (user.loginAttempts || 0) + 1;
    
    // Lock account after 5 failed attempts
    if (user.loginAttempts >= 5) {
      user.lockedUntil = new Date(Date.now() + 30 * 60 * 1000).toISOString(); // 30 minutes
      users.set(user.id, user);
      
      logger.logSecurity('Account locked due to failed attempts', { 
        email, 
        userId: user.id, 
        attempts: user.loginAttempts 
      }, req);
      
      return res.status(423).json({
        success: false,
        error: 'Account locked',
        message: 'Account locked due to too many failed login attempts'
      });
    }
    
    users.set(user.id, user);
    
    logger.logSecurity('Failed login attempt', { 
      email, 
      userId: user.id, 
      attempts: user.loginAttempts 
    }, req);
    
    return res.status(401).json({
      success: false,
      error: 'Invalid credentials',
      message: 'Email or password is incorrect'
    });
  }
  
  // Reset login attempts on successful login
  user.loginAttempts = 0;
  user.lockedUntil = null;
  user.lastLogin = new Date().toISOString();
  users.set(user.id, user);
  
  // Generate token
  const token = generateToken({
    userId: user.id,
    email: user.email,
    role: user.role,
    permissions: user.permissions
  });
  
  // Log successful login
  logger.audit('user_login', 'user', user.id, {
    email,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  
  res.json({
    success: true,
    message: 'Login successful',
    data: {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        permissions: user.permissions,
        lastLogin: user.lastLogin
      },
      token
    }
  });
}));

/**
 * @route   POST /api/auth/logout
 * @desc    Logout user (invalidate token)
 * @access  Private
 */
router.post('/logout', authenticate, catchAsync(async (req, res) => {
  // In a production app, you would add the token to a blacklist
  // For now, we'll just log the logout
  
  logger.audit('user_logout', 'user', req.user.id, {
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  
  res.json({
    success: true,
    message: 'Logged out successfully'
  });
}));

/**
 * @route   GET /api/auth/me
 * @desc    Get current user info
 * @access  Private
 */
router.get('/me', authenticate, catchAsync(async (req, res) => {
  const user = findUserById(req.user.id);
  
  if (!user) {
    throw new AppError('User not found', 404);
  }
  
  res.json({
    success: true,
    data: {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        permissions: user.permissions,
        createdAt: user.createdAt,
        lastLogin: user.lastLogin
      }
    }
  });
}));

/**
 * @route   POST /api/auth/change-password
 * @desc    Change user password
 * @access  Private
 */
router.post('/change-password', authenticate, changePasswordValidation, catchAsync(async (req, res) => {
  // Check validation results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array()
    });
  }
  
  const { currentPassword, newPassword } = req.body;
  const user = findUserById(req.user.id);
  
  if (!user) {
    throw new AppError('User not found', 404);
  }
  
  // Verify current password
  const isCurrentPasswordValid = await bcrypt.compare(currentPassword, user.password);
  if (!isCurrentPasswordValid) {
    logger.logSecurity('Invalid current password in change attempt', { userId: req.user.id }, req);
    return res.status(400).json({
      success: false,
      error: 'Invalid current password'
    });
  }
  
  // Hash new password
  const saltRounds = 12;
  const hashedNewPassword = await bcrypt.hash(newPassword, saltRounds);
  
  // Update password
  user.password = hashedNewPassword;
  user.passwordChangedAt = new Date().toISOString();
  users.set(req.user.id, user);
  
  // Log password change
  logger.audit('password_changed', 'user', req.user.id, {
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  
  res.json({
    success: true,
    message: 'Password changed successfully'
  });
}));

/**
 * @route   POST /api/auth/refresh
 * @desc    Refresh JWT token
 * @access  Private
 */
router.post('/refresh', authenticate, catchAsync(async (req, res) => {
  const user = findUserById(req.user.id);
  
  if (!user || !user.isActive) {
    throw new AppError('User not found or inactive', 404);
  }
  
  // Generate new token
  const token = generateToken({
    userId: user.id,
    email: user.email,
    role: user.role,
    permissions: user.permissions
  });
  
  res.json({
    success: true,
    message: 'Token refreshed successfully',
    data: { token }
  });
}));

module.exports = router;
