/**
 * User Management Routes
 * CRUD operations for user management with proper authorization
 */

const express = require('express');
const { body, query, validationResult } = require('express-validator');
const router = express.Router();

const { authorize, requirePermission, requireOwnership } = require('../middleware/auth');
const { catchAsync, AppError } = require('../middleware/errorHandler');
const logger = require('../utils/logger');

// In-memory user store (same as auth routes - replace with database)
const users = new Map();

// Helper functions
const findUserById = (id) => {
  const user = users.get(id);
  return user ? { id, ...user } : null;
};

const findUserByEmail = (email) => {
  for (const [id, user] of users) {
    if (user.email === email) {
      return { id, ...user };
    }
  }
  return null;
};

// Validation rules
const updateUserValidation = [
  body('name')
    .optional()
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Name must be between 2 and 50 characters'),
  body('email')
    .optional()
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('role')
    .optional()
    .isIn(['user', 'admin', 'moderator'])
    .withMessage('Invalid role specified'),
  body('isActive')
    .optional()
    .isBoolean()
    .withMessage('isActive must be a boolean value')
];

const queryValidation = [
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('Page must be a positive integer'),
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 })
    .withMessage('Limit must be between 1 and 100'),
  query('search')
    .optional()
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Search term must be between 1 and 100 characters'),
  query('role')
    .optional()
    .isIn(['user', 'admin', 'moderator'])
    .withMessage('Invalid role filter'),
  query('isActive')
    .optional()
    .isBoolean()
    .withMessage('isActive filter must be a boolean')
];

/**
 * @route   GET /api/users
 * @desc    Get all users (with pagination and filtering)
 * @access  Private (Admin or users with 'read' permission)
 */
router.get('/', requirePermission('read'), queryValidation, catchAsync(async (req, res) => {
  // Check validation results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array()
    });
  }
  
  const {
    page = 1,
    limit = 10,
    search = '',
    role,
    isActive,
    sortBy = 'createdAt',
    sortOrder = 'desc'
  } = req.query;
  
  // Convert users Map to array
  let userList = Array.from(users.entries()).map(([id, user]) => ({
    id,
    ...user,
    password: undefined // Never return password
  }));
  
  // Apply filters
  if (search) {
    const searchLower = search.toLowerCase();
    userList = userList.filter(user => 
      user.name.toLowerCase().includes(searchLower) ||
      user.email.toLowerCase().includes(searchLower)
    );
  }
  
  if (role) {
    userList = userList.filter(user => user.role === role);
  }
  
  if (isActive !== undefined) {
    userList = userList.filter(user => user.isActive === (isActive === 'true'));
  }
  
  // Apply sorting
  userList.sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];
    
    if (sortBy === 'createdAt' || sortBy === 'lastLogin') {
      aValue = new Date(aValue || 0);
      bValue = new Date(bValue || 0);
    }
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  // Apply pagination
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + parseInt(limit);
  const paginatedUsers = userList.slice(startIndex, endIndex);
  
  // Calculate pagination info
  const totalUsers = userList.length;
  const totalPages = Math.ceil(totalUsers / limit);
  const hasNextPage = endIndex < totalUsers;
  const hasPrevPage = startIndex > 0;
  
  // Log the query for audit
  logger.audit('users_queried', 'users', req.user.id, {
    filters: { search, role, isActive },
    pagination: { page, limit },
    resultCount: paginatedUsers.length
  });
  
  res.json({
    success: true,
    data: {
      users: paginatedUsers,
      pagination: {
        currentPage: parseInt(page),
        totalPages,
        totalUsers,
        hasNextPage,
        hasPrevPage,
        limit: parseInt(limit)
      },
      filters: {
        search,
        role,
        isActive,
        sortBy,
        sortOrder
      }
    }
  });
}));

/**
 * @route   GET /api/users/:id
 * @desc    Get user by ID
 * @access  Private (Admin or own profile)
 */
router.get('/:id', requireOwnership('id'), catchAsync(async (req, res) => {
  const { id } = req.params;
  const user = findUserById(id);
  
  if (!user) {
    throw new AppError('User not found', 404);
  }
  
  // Remove sensitive information
  const { password, ...userInfo } = user;
  
  res.json({
    success: true,
    data: { user: userInfo }
  });
}));

/**
 * @route   PUT /api/users/:id
 * @desc    Update user
 * @access  Private (Admin or own profile with restrictions)
 */
router.put('/:id', requireOwnership('id'), updateUserValidation, catchAsync(async (req, res) => {
  // Check validation results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array()
    });
  }
  
  const { id } = req.params;
  const { name, email, role, isActive } = req.body;
  
  const user = findUserById(id);
  if (!user) {
    throw new AppError('User not found', 404);
  }
  
  // Check if email is already taken by another user
  if (email && email !== user.email) {
    const existingUser = findUserByEmail(email);
    if (existingUser && existingUser.id !== id) {
      return res.status(409).json({
        success: false,
        error: 'Email already exists',
        message: 'A user with this email already exists'
      });
    }
  }
  
  // Only admins can change role and isActive status
  if ((role || isActive !== undefined) && req.user.role !== 'admin') {
    logger.logSecurity('Unauthorized role/status change attempt', {
      userId: req.user.id,
      targetUserId: id,
      attemptedChanges: { role, isActive }
    }, req);
    
    return res.status(403).json({
      success: false,
      error: 'Insufficient permissions',
      message: 'Only administrators can change user role or active status'
    });
  }
  
  // Update user fields
  const updatedUser = {
    ...user,
    ...(name && { name }),
    ...(email && { email }),
    ...(role && { role }),
    ...(isActive !== undefined && { isActive }),
    updatedAt: new Date().toISOString()
  };
  
  // Update permissions based on role
  if (role) {
    updatedUser.permissions = role === 'admin' 
      ? ['read', 'write', 'delete', 'admin']
      : ['read', 'write'];
  }
  
  users.set(id, updatedUser);
  
  // Log the update
  logger.audit('user_updated', 'user', id, {
    updatedBy: req.user.id,
    changes: { name, email, role, isActive },
    ip: req.ip
  });
  
  // Remove sensitive information from response
  const { password, ...userInfo } = updatedUser;
  
  res.json({
    success: true,
    message: 'User updated successfully',
    data: { user: { id, ...userInfo } }
  });
}));

/**
 * @route   DELETE /api/users/:id
 * @desc    Delete user (soft delete)
 * @access  Private (Admin only)
 */
router.delete('/:id', authorize(['admin']), catchAsync(async (req, res) => {
  const { id } = req.params;
  
  // Prevent admin from deleting themselves
  if (id === req.user.id) {
    return res.status(400).json({
      success: false,
      error: 'Cannot delete own account',
      message: 'Administrators cannot delete their own accounts'
    });
  }
  
  const user = findUserById(id);
  if (!user) {
    throw new AppError('User not found', 404);
  }
  
  // Soft delete by setting isActive to false
  const updatedUser = {
    ...user,
    isActive: false,
    deletedAt: new Date().toISOString(),
    deletedBy: req.user.id
  };
  
  users.set(id, updatedUser);
  
  // Log the deletion
  logger.audit('user_deleted', 'user', id, {
    deletedBy: req.user.id,
    userEmail: user.email,
    ip: req.ip
  });
  
  res.json({
    success: true,
    message: 'User deleted successfully'
  });
}));

/**
 * @route   POST /api/users/:id/activate
 * @desc    Reactivate a deactivated user
 * @access  Private (Admin only)
 */
router.post('/:id/activate', authorize(['admin']), catchAsync(async (req, res) => {
  const { id } = req.params;
  
  const user = findUserById(id);
  if (!user) {
    throw new AppError('User not found', 404);
  }
  
  // Reactivate user
  const updatedUser = {
    ...user,
    isActive: true,
    reactivatedAt: new Date().toISOString(),
    reactivatedBy: req.user.id,
    deletedAt: undefined,
    deletedBy: undefined
  };
  
  users.set(id, updatedUser);
  
  // Log the reactivation
  logger.audit('user_reactivated', 'user', id, {
    reactivatedBy: req.user.id,
    userEmail: user.email,
    ip: req.ip
  });
  
  res.json({
    success: true,
    message: 'User reactivated successfully'
  });
}));

/**
 * @route   GET /api/users/stats
 * @desc    Get user statistics
 * @access  Private (Admin only)
 */
router.get('/stats/overview', authorize(['admin']), catchAsync(async (req, res) => {
  const allUsers = Array.from(users.values());
  
  const stats = {
    total: allUsers.length,
    active: allUsers.filter(user => user.isActive).length,
    inactive: allUsers.filter(user => !user.isActive).length,
    byRole: {
      admin: allUsers.filter(user => user.role === 'admin').length,
      moderator: allUsers.filter(user => user.role === 'moderator').length,
      user: allUsers.filter(user => user.role === 'user').length
    },
    recentRegistrations: {
      today: allUsers.filter(user => {
        const userDate = new Date(user.createdAt);
        const today = new Date();
        return userDate.toDateString() === today.toDateString();
      }).length,
      thisWeek: allUsers.filter(user => {
        const userDate = new Date(user.createdAt);
        const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
        return userDate >= weekAgo;
      }).length,
      thisMonth: allUsers.filter(user => {
        const userDate = new Date(user.createdAt);
        const monthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
        return userDate >= monthAgo;
      }).length
    }
  };
  
  res.json({
    success: true,
    data: { stats }
  });
}));

module.exports = router;
